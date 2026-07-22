# Stardew Valley Tool

[English](README.md) | [简体中文](README.zh.md) | [Português](README.pt.md) | [日本語](README.jp.md)

Aplicación de escritorio para Windows que permite consultar y editar de forma segura determinados datos de las partidas guardadas de Stardew Valley. Utiliza la ubicación estándar de partidas de Windows y el ejecutable de lanzamiento no requiere instalar Python.

## Descarga

Descargue `StardewValleySaveManager.exe` desde la [última versión de GitHub](https://github.com/fyihang/StardewValleyTool/releases). No se necesita una instalación de Python para usar el ejecutable de lanzamiento.

## Elementos que se pueden editar

- Nombre del granjero
- Nombre de la granja
- Cosa favorita
- Nombres de los animales existentes, incluido el caballo cuando esté presente
- Nombres y cosas favoritas de los jornaleros existentes mediante un selector (el nombre de la granja sigue siendo un ajuste exclusivo del propietario)

La interfaz está disponible en inglés, chino simplificado, portugués, español y japonés. Los tipos de animales se traducen al idioma seleccionado; los tipos desconocidos de animales de mods permanecen visibles con su valor original del juego.

## Protección de las partidas

Al iniciarse, la aplicación busca el directorio estándar de Windows:

```text
%appdata%\StardewValley\Saves
```

Use **Elegir directorio de partidas** para seleccionar otra raíz de partidas únicamente durante la sesión actual. Esta elección no se guarda; al abrir de nuevo la aplicación, se volverá a utilizar el directorio estándar.

Una partida solo se reconoce cuando su carpeta contiene `SaveGameInfo` y el archivo principal que lleva el mismo nombre que la carpeta. La información del propietario compartida por ambos archivos se actualiza en los dos. Los jornaleros y animales se editan únicamente en el archivo principal, donde se almacenan esos registros.

Antes de escribir, la aplicación copia ambos archivos en `.svt-backups/<marca de tiempo UTC>/` dentro de la carpeta de la partida. Valida los XML temporales antes de sustituir los originales y comprueba el resultado guardado después. Si se produce un error durante la operación, restaura ambos archivos originales desde la copia de seguridad.

## Uso

1. Cierre completamente Stardew Valley.
2. Inicie `StardewValleySaveManager.exe`.
3. Seleccione una partida en la lista de la izquierda.
4. Edite los campos del propietario; si existen jornaleros, seleccione uno en la lista; haga doble clic en el nombre de un animal para cambiarlo.
5. Seleccione **Guardar cambios** y confirme que el juego está cerrado.

En el primer uso, cree una copia independiente de una carpeta de partida y pruebe los cambios allí. Conserve el directorio `.svt-backups` generado hasta verificar la partida editada dentro del juego.

## Código fuente

Para ejecutar desde el código fuente, instale Python 3.11 o posterior y ejecute lo siguiente desde la raíz del repositorio:

```powershell
$env:PYTHONPATH = "src"
python src\__main__.py
```

## Licencia

Distribuido bajo la [licencia MIT](LICENSE).
