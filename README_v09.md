# AutoSleeper v0.9 — Build portable de Windows

Este ZIP es una **actualización para tu repositorio local**, no un programa ya compilado. No reemplaza la interfaz, las preferencias ni la lógica del apagado real.

## Instalar los archivos

1. Cierra AutoSleeper desde **Exit** en el System Tray.
2. Guarda un commit de seguridad: `git add . ; git commit -m "Save state before portable build"` (si hay cambios por guardar).
3. Extrae el contenido del ZIP en `C:\Python\Projects\AutoSleeper`, respetando las carpetas `core` y `tests`.
4. En la terminal PowerShell de VS Code ejecuta:

```powershell
.\.venv\Scripts\python.exe install_v09.py
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\build_portable.ps1
```

Si Windows bloquea scripts PowerShell por política, **no necesitas deshabilitar la política global**. Prueba desde la terminal actual:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\build_portable.ps1
```

El instalador solo modifica dos líneas funcionales en `main.py`: añade el import del cargador QSS y sustituye la lectura QSS simple por la lectura con rutas absolutas. Hace una copia de seguridad en la carpeta temporal `AutoSleeper_backups`. La actualización es idempotente; si `main.py` tiene cambios incompatibles, el instalador falla sin sobreescribirlo.

## Resultado

Archivo generado en:

```
C:\Python\Projects\AutoSleeper\dist\AutoSleeper.exe
```

PyInstaller **debe ejecutarse en Windows** para generar un `.exe` de Windows; no es un compilador cruzado. Se utiliza `--onefile` y `--windowed` mediante `AutoSleeper-portable.spec`.

El paquete incluye los iconos `.png/.ico` y demás imágenes habituales de `assets/`, además de `ui/*.qss` respetando la jerarquía. Los `.py` de `core/` y `ui/` son recogidos automáticamente por PyInstaller. `QSettings` continúa almacenando las preferencias en el perfil de Windows.

El archivo `.ico` se incrusta en el ejecutable y se incluye también como recurso de ejecución, para que tanto la barra de tareas como el System Tray encuentren el icono.

## Comprobar ANTES de activar el apagado real

**Pasa Real shutdown a OFF** al ejecutar el EXE. En la implementación actual, el usuario lo configuró en ON por defecto: un temporizador de prueba podría apagar realmente Windows.

1. Copia `dist\AutoSleeper.exe` al escritorio o a otra carpeta, **sin** copiar `assets/`, `ui/`, ni `.venv/`.
2. Ejecútalo; comprueba cabecera, logo y footer, estilos Matrix, icono de tareas y bandeja.
3. Selecciona español y cierra completamente. Reinicia y verifica que lo recuerda.
4. En modo de prueba OFF: establece 10 segundos. Confirma que muestra el estado completado y **no apaga** Windows.
5. Con un temporizador de prueba activo, cierra la ventana con X. Comprueba el icono de bandeja y restaura con doble clic.
6. Con la aplicación abierta, haz doble clic en el EXE. Debe restaurar la ventana existente sin abrir un segundo temporizador.
7. Desde otra carpeta y con un temporizador de prueba activo, suspende Windows y reanuda. Comprueba que la cuenta atrás se canceló.
8. Solo después de revisar todo, considera una prueba real con el trabajo guardado y sin documentos pendientes.

## Errores de inicio

El ejecutable de distribución oculta la consola. Para diagnosticar problemas, recompila con:

```powershell
.\build_portable.ps1 -Console -SkipTests
```

Ejecuta `dist\AutoSleeper.exe` desde PowerShell para consultar el error. Después recompila sin `-Console` para publicar la versión definitiva.

Si la compilación informa de un archivo ausente (`assets/logo.png`, `assets/blackout_logo.png`, `assets/AutoSleeper_black.ico`, `ui/styles.qss`), comprueba las rutas en el proyecto; la compilación falla intencionadamente en lugar de generar una aplicación visualmente incompleta.

## Git y GitHub

Los directorios `build/` y `dist/` deben estar en `.gitignore`; **no subas** los ejecutables al historial del código fuente. Puedes subir el EXE como archivo descargable en GitHub Releases cuando esté validado.

```powershell
git add main.py core/bundle_resources.py install_v09.py AutoSleeper-portable.spec build_portable.ps1 requirements-build.txt tests/test_bundle_resources.py
git commit -m "Add portable Windows build with PyInstaller"
git push
```
