"""User interface preferences for AutoSleeper.

On Windows, QSettings normally stores these values in the current user's
registry under Software/BlackoutStudios/AutoSleeper.

Intentionally excludes shutdown permissions and running timer state.
"""

from collections.abc import Collection

from PySide6.QtCore import QSettings


class Preferences:
    ORGANIZATION = "BlackoutStudios"
    APPLICATION = "AutoSleeper"
    LANGUAGE_KEY = "ui/language"
    DEFAULT_LANGUAGE = "en"

    def __init__(self, settings: QSettings | None = None):
        self._settings = (
            settings
            if settings is not None
            else QSettings(self.ORGANIZATION, self.APPLICATION)
        )
        self._settings.setFallbacksEnabled(False)

    #region LANGUAGE

    def load_language(self, supported_languages: Collection[str]) -> str:
        language = self._settings.value(
            self.LANGUAGE_KEY,
            self.DEFAULT_LANGUAGE,
            type=str,
        )

        return (
            language
            if language in supported_languages
            else self.DEFAULT_LANGUAGE
        )

    def save_language(self, language: str) -> None:
        if not isinstance(language, str) or not language:
            raise ValueError("Language code cannot be empty")

        self._settings.setValue(self.LANGUAGE_KEY, language)
        self._settings.sync()

    #endregion
