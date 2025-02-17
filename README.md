# Auto Commit Tool

Una herramienta de línea de comandos en Python para automatizar el proceso de commits en Git. Permite:

- Agregar todos los cambios en el repositorio.
- Obtener el diff actual y, opcionalmente, generar un mensaje de commit utilizando la API de OpenAI.
- Realizar el commit.
- (Opcional) Hacer push al repositorio remoto.

## Requisitos

- Python 3.6 o superior.
- Git instalado en el sistema.
- Opcional: [OpenAI Python package](https://pypi.org/project/openai/) (si se desea usar la funcionalidad de generación automática de mensajes).

## Instalación

1. Clona el repositorio:

   ```bash
   git clone https://github.com/tu_usuario/auto-commit-tool.git
   cd auto-commit-tool