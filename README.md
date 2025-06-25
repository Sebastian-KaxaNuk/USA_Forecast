# USA_Forecast
Bienvenido al proyecto USA_Forecast. Para asegurar una gestión eficiente y ordenada de los archivos y la configuración del entorno, sigue las siguientes instrucciones detalladas.

## Estructura de Carpetas

Mantener una estructura de carpetas organizada es crucial para la eficiencia del proyecto. Organiza tus archivos de la siguiente manera:

- **Carpeta `Output`**: Esta carpeta debe contener todos los archivos relacionados con los datos de mercado y el archivo final:
  - **Subcarpeta `Tickers`**: Archivos csv de las stocks que nos interesen, contienen OHLC, volumen y los cálculos necesarios para el análisis.
  
- **Carpeta `Config`**: Esta carpeta debe contener el template de parámetros en formato excel, llamado "parameters_configuration.xlsx".

## Configuración del Entorno y Dependencias

Para configurar tu entorno y asegurarte de que todas las dependencias necesarias están instaladas, sigue estos pasos:

1. **Descargar Anaconda**: Descarga la versión más reciente de Anaconda desde su [sitio web oficial](https://www.anaconda.com/products/distribution). Asegúrate de elegir la versión que corresponda a tu sistema operativo.

2. **Abrir Anaconda Prompt**: Una vez instalado Anaconda, inicia Anaconda Prompt desde tu menú de inicio.

3. **Crear un Nuevo Environment con Python 3.12**: En Anaconda Prompt, crea un nuevo environment llamado `usa_forecast` con Python 3.12 utilizando el siguiente comando:
   ```bash
   conda create --name usa_forecast python=3.12

4. **Activar el Environment**: Activa el environment recién creado con el comando:
   ```bash
   conda activate usa_forecast
   
5. **Cambiar al Directorio del Repositorio**: Navega al directorio donde está clonado el repositorio utilizando el comando cd. Por ejemplo:    
    ```bash
    cd C:\Users\TuUsuario\Documents\USA_Forecast
    
6. **Instalar PDM**: Dentro del environment activado, instala PDM utilizando pip con el siguiente comando:
    ```bash
    pip install pdm
    
7. **Instalar Dependencias con PDM**: Ejecuta pdm install para instalar todas las dependencias del proyecto definidas en el archivo pyproject.toml. Usa el siguiente comando:
    ```bash
    pdm install

## Consideraciones post instalacion

1. Una vez realizados los pasos previos, ya no es necesario hacer todo, los pasos que se explicaron anteriormente
son para realizar la instalacion de dependencias y librerias en un entorno nuevo y libre de paqueterias, esto con la 
finalidad de evitar conflicto entre ellas. 

2. **¿Qué es lo que tendria que hacer?**: Lo único que se tiene que hacer cada que se quiera correr el código, es 
abrir Anaconda Navigator, abrir el environment (eso se puede hacer en Home, en el dropdown que se encuentra arriba, el dropdown derecho y seleccionamos backtesting),
despues de eso, abrimos spyder y finalmente, seleccionamos el directorio de trabajo, seleccionando la carpeta que se encuentra en la parte superior derecha, para buscar
la carpeta donde clonamos el repositorio.

## Instructivo de uso del proyecto USA_Forecast

1. **Abrir nuestro IDE**: Una vez hecho la instalación de las librerias con los pasos anterior, vamos a abrir nuestro IDE.

2. **Seteamos nuestro environment**: En spyder, nos vamos a la barra de navegación, seleccionamos tools, despues preferences,
despues python interpreter, seleccionamos la opción de "Use the following Python Interpreter" y seleccionamos el environmente que creamos.
Despues, reiniciamos la consola. En el caso de PyCharm, cuando seleccionamos el proyecto, nos dirigimos a la parte inferior derecha, y seleccionamos Add new environment.

3. **Seteamos el CD**: En spyder, en la parte superior derecha, seleccionamos el icono de la carpeta, y buscamos el directorio donde clonamos el repositorio.
En el caso de PyCharm, solo abrimos el proyecto.

4. **Correr main**: Solo tenemos que correr main, hay que asegurarnos de que llenamos nuestro archivo excel que va en la carpeta de Config, llamado "parameters_configuration.xlsx".
