# Scrapy settings for weworkremotely project
import os 

# --- CONFIGURACIÓN GENERAL ---
BOT_NAME = 'weworkremotely'
SPIDER_MODULES = ['weworkremotely.spiders']
NEWSPIDER_MODULE = ['weworkremotely.spiders']


# --- CONFIGURACIÓN DE "CORTESÍA" ---
USER_AGENT = 'WeworkJobScraper (Educational project; +your-contact@email.com)'
ROBOTSTXT_OBEY = True
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False # Ponlo a True si quieres ver los logs del throttle


# --- CONFIGURACIÓN DE PIPELINES (¡ACTIVADAS!) ---
ITEM_PIPELINES = {
   # 1. Limpiar datos (prioridad 100)
   'weworkremotely.pipelines.WeworkDataCleaningPipeline': 100,
   
   # 2. Enviar datos limpios a ES (prioridad 300)
   'weworkremotely.pipelines.ElasticsearchPipeline': 300,
}


# --- CONFIGURACIÓN PERSONALIZADA ---

# Encuentra la carpeta que contiene 'settings.py'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ELASTICSEARCH_HOST = 'localhost'
ELASTICSEARCH_PORT = 9200
ELASTICSEARCH_INDEX = 'wework_jobs_final' # El nombre de tu índice

# Construye una ruta absoluta para 'es_mapping.json'
ELASTICSEARCH_MAPPING_PATH = os.path.join(BASE_DIR, 'es_mapping.json')


# --- OTRAS CONFIGURACIONES ESTÁNDAR ---
COOKIES_ENABLED = False
TELNETCONSOLE_ENABLED = False
FEED_EXPORT_ENCODING = 'utf-8'