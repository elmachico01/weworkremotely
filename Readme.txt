WORKSEEK - SCRAPER & BUSCADOR DE EMPLEOS

Este proyecto es una solución completa de tipo ETL (Extract, Transform, Load). Extrae ofertas de trabajo remoto de We Work Remotely, limpia los datos, extrae habilidades técnicas automáticamente y las indexa en un motor de búsqueda (Elasticsearch) para ser visualizadas en una aplicación web moderna.

ESTRUCTURA DEL PROYECTO:
A continuación se muestra la organización de los archivos. Es importante entenderla para saber desde dónde ejecutar los comandos.
weworkremotely/                  <-- Carpeta Raíz del Proyecto (donde está scrapy.cfg)
│
├── scrapy.cfg                   # Archivo de configuración de despliegue de Scrapy
│
└── weworkremotely/              # Paquete principal de Python
    ├── __init__.py
    ├── app.py                   # Aplicación Web (Flask + Backend API)
    ├── items.py                 # Definición del modelo de datos (JobItem)
    ├── middlewares.py           # Middlewares de Scrapy
    ├── pipelines.py             # Limpieza de datos y envío a Elasticsearch
    ├── settings.py              # Configuración del Spider y constantes
    ├── es_mapping.json          # Esquema de la base de datos Elasticsearch
    ├── skills_names.json        # Lista de keywords para detectar habilidades
    │
    ├── spiders/                 # Carpeta de los "Arañas" (Spiders)
    │   ├── __init__.py
    │   └── wework_spider.py     # El código que navega y descarga los datos
    │
    ├── static/                  # Archivos estáticos del Frontend
    │   ├── css/
    │   │   └── style.css        # Estilos de la web
    │   ├── js/
    │   │   └── main.js          # Lógica del buscador en el navegador
    │   └── workseek_logo.png    # Logo de la aplicación
    │
    └── templates/               # Plantillas HTML (Flask)
        ├── index.html           # Página principal con el buscador
        └── search_results.html  # Vista de resultados


GUÍA DE INSTALACIÓN:
1. Configuración de la Base de Datos (Docker)
Antes de nada, necesitas ejecutar Elasticsearch. Usaremos la versión recomendada 8.14.0. Descargar la imagen Primero, asegúrate de descargar la imagen oficial de Elasticsearch ejecutando el siguiente comando en tu terminal: docker pull docker.elastic.co/elasticsearch/elasticsearch:8.14.0
Una vez tengas la imagen, es muy importante incluir la opción de deshabilitar la seguridad (xpack.security.enabled=false) porque tu código actual de Python se conecta vía HTTP simple, no HTTPS.
Comando:
docker run --name es-workseek -d -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" docker.elastic.co/elasticsearch/elasticsearch:8.14.0

2. Crear un Entorno Virtual (Python)
Es una buena práctica aislar las librerías del proyecto. Abre tu terminal en la carpeta raíz (weworkremotely/) y ejecuta
En Windows:
python -m venv venv
venv\Scripts\activate
En Mac/Linux:
python3 -m venv venv
source venv/bin/activate

3. Instalar las Dependencias
Crea un archivo llamado requirements.txt en la raíz con el siguiente contenido:
scrapy
flask
elasticsearch==8.14.0
beautifulsoup4
dateparser
lxml
itemadapter

Luego,instala todo con:
pip install -r requirements.txt

CÓMO EJECUTAR EL PROYECTO:
El proyecto tiene dos partes: el Scraper (que baja los datos) y la Web App (que los muestra).

Paso 1: Ejecutar el Scraper (Llenar la Base de Datos)
Este comando navegará por We Work Remotely, descargará los trabajos, los limpiará y los guardará en Elasticsearch.
Asegúrate de estar en la carpeta raíz (donde está scrapy.cfg) y ejecuta:
scrapy crawl wework

Paso 2: Lanzar la Aplicación Web
Una vez que tengas datos, levanta el servidor web Flask.
python weworkremotely/app.py
Si todo va bien, verás un mensaje como: Running on http://127.0.0.1:5000

Paso 3: Usar la Aplicación
Abre tu navegador web y ve a: http://127.0.0.1:5000
•Usa la barra lateral para filtrar por Categoría, País, Salario o Skills.
•Escribe en el buscador principal para buscar por texto libre

