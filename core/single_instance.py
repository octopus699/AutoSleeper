"""Prevent duplicate AutoSleeper processes and restore the first window.

QLockFile guarantees exclusive ownership; QLocalServer/QLocalSocket carry the
"SHOW" request from a second launch to the running primary instance.
"""

import hashlib
import time
from pathlib import Path

from PySide6.QtCore import QObject, QLockFile, QStandardPaths, Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket


class SingleInstanceGuard(QObject):
    activation_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Store the lock outside the portable application directory, so a
        # read-only directory does not prevent the program from launching.
        app_data = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppLocalDataLocation
        )
        if not app_data:
            app_data = str(Path.home() / ".autosleeper")

        self.data_dir = Path(app_data)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        user_scoped_id = hashlib.sha256(
            str(self.data_dir).encode("utf-8")
        ).hexdigest()[:16]
        self.server_name = f"BlackoutStudios.AutoSleeper.{user_scoped_id}"

        self.lock = QLockFile(str(self.data_dir / "instance.lock"))
        # A running desktop app can hold the lock for hours or days.
        self.lock.setStaleLockTime(0)
        self.is_primary = self.lock.tryLock(0)
        self.server = None

        if self.is_primary:
            self.server = QLocalServer(self)

            if not self.server.listen(self.server_name):
                # On Unix, a crash can leave a stale local socket pathname.
                # We hold the lock, so no other instance owns that socket.
                QLocalServer.removeServer(self.server_name)
                if not self.server.listen(self.server_name):
                    error = self.server.errorString()
                    self.close()
                    raise RuntimeError(
                        f"Cannot start AutoSleeper local server: {error}"
                    )

            self.server.newConnection.connect(self._accept_connections)

    #region COMMUNICATION

    def _accept_connections(self):
        if self.server is None:
            return

        while self.server.hasPendingConnections():
            connection = self.server.nextPendingConnection()
            if connection is None:
                break

            connection.readyRead.connect(
                lambda conn=connection: self._read_request(conn)
            )
            connection.disconnected.connect(connection.deleteLater)

            if connection.bytesAvailable() > 0:
                self._read_request(connection)

    def _read_request(self, connection):
        data = bytes(connection.readAll())
        if b"SHOW" in data:
            self.activation_requested.emit()
            connection.write(b"OK")
            connection.flush()
            connection.disconnectFromServer()

    def activate_existing(self) -> bool:
        """Tell the primary instance to restore its window; return on ACK."""
        for _ in range(6):
            connection = QLocalSocket()
            connection.connectToServer(self.server_name)

            if connection.waitForConnected(350):
                connection.write(b"SHOW\n")
                connection.flush()
                connection.waitForBytesWritten(350)

                if connection.waitForReadyRead(350):
                    acknowledged = b"OK" in bytes(connection.readAll())
                    connection.disconnectFromServer()
                    return acknowledged

                connection.disconnectFromServer()

            connection.abort()
            time.sleep(0.1)

        return False

    #endregion

    #region LIFECYCLE

    def close(self):
        if self.server is not None:
            self.server.close()
            self.server = None

        if self.is_primary:
            self.lock.unlock()
            self.is_primary = False

    #endregion
