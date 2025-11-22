import re
import dateparser
from bs4 import BeautifulSoup
from itemadapter import ItemAdapter
from elasticsearch import Elasticsearch
import json
import os
from datetime import datetime
import scrapy
import logging

# --- 1. NUESTRO DICCIONARIO DE HABILIDADES ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, 'skills_names.json')

try:
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        SKILL_LIST = json.load(f)
except FileNotFoundError:
    # Fallback di sicurezza se il file non si trova (opzionale)
    print(f"ATTENTION: File {JSON_PATH} not found.")
# Patrón Regex: \b(Python|React...)\b -> busca palabras completas, ignora mayúsculas
SKILL_REGEX = re.compile(r'\b(' + '|'.join(re.escape(s) for s in SKILL_LIST) + r')\b')
# Mapa para estandarizar (ej. "python" -> "Python")
SKILL_MAP = {s.lower(): s for s in SKILL_LIST}


class WeworkDataCleaningPipeline:
    """
    Pipeline para el Post-Procesamiento (según las diapositivas del profesor):
    1. Limpieza de Fechas (con dateparser)
    2. Limpieza de Descripción (con BeautifulSoup)
    3. Extracción de Habilidades (con Regex)
    """
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # --- 1. Limpieza de Fecha (con dateparser) ---
        posted_date_str = adapter.get('posted_date')
        if posted_date_str:
            # "A few minutes ago", "New" -> fecha actual
            if "minute" in posted_date_str or "New" in posted_date_str:
                dt = datetime.utcnow()
            else:
                # "19d ago", "3h ago" -> fecha parseada
                dt = dateparser.parse(posted_date_str)
            
            if dt:
                adapter['posted_date'] = dt.isoformat()
            else:
                adapter['posted_date'] = None # Mejor None que un texto extraño

        # --- 2. Limpieza de Descripción y Extracción de Habilidades (con BeautifulSoup) ---
        description_html = adapter.get('description')
        if description_html:
            # A. Limpieza HTML
            soup = BeautifulSoup(description_html, 'lxml')
            clean_text = soup.get_text(separator=' ', strip=True)
            adapter['description'] = clean_text # Sobrescribimos el HTML con el texto limpio
            
            # B. Extracción de Habilidades
            # Encuentra todas las coincidencias únicas en el texto limpio
            found_skills = set(SKILL_REGEX.findall(clean_text))
            
            # Estandariza (ej. "python", "Python", "PYTHON" -> "Python")
            adapter['skills'] = sorted(list(set(
                SKILL_MAP[skill.lower()] for skill in found_skills
            )))
        else:
            adapter['description'] = "" # Texto vacío
            adapter['skills'] = []    # Lista vacía
        logo_style_str = adapter.get('logo_url')
        if logo_style_str:
            # Busca el patrón url(...) en la cadena de estilo
            match = re.search(r'url\((.*?)\)', logo_style_str)
            if match:
                # Extrae la URL (grupo 1) y limpia cualquier comilla
                adapter['logo_url'] = match.group(1).strip('\'"')
            else:
                adapter['logo_url'] = "" # ¿Encontrado estilo pero no URL? Mejor vacío.
        else:
            adapter['logo_url'] = "" # Ningún estilo encontrado
        # Limpieza de campos opcionales (si no se encuentran)
        adapter['company_description'] = adapter.get('company_description', "")
        adapter['job_type'] = adapter.get('job_type', "")
        adapter['category'] = adapter.get('category', "")
        
        # --- CAMPO AÑADIDO ---
        adapter['salary'] = adapter.get('salary', "")
        
        return item


class ElasticsearchPipeline:
    """
    Pipeline final: envía el Item (ya limpio) a Elasticsearch
    """
    def __init__(self, es_host, es_port, es_index, es_mapping_path):
        self.es_host = es_host
        self.es_port = es_port
        self.es_index = es_index
        self.es_mapping_path = es_mapping_path
        self.es_client = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            es_host=crawler.settings.get('ELASTICSEARCH_HOST'),
            es_port=crawler.settings.get('ELASTICSEARCH_PORT'),
            es_index=crawler.settings.get('ELASTICSEARCH_INDEX'),
            es_mapping_path=crawler.settings.get('ELASTICSEARCH_MAPPING_PATH', 'es_mapping.json')
        )
    # ... (todas las importaciones al principio del archivo, incluido 'import logging') ...

    def open_spider(self, spider):
        # Conexión
        self.es_client = Elasticsearch([{'host': self.es_host, 'port': self.es_port, 'scheme': 'http'}])
        spider.log(f"Connected to Elasticsearch at {self.es_host}:{self.es_port}")
        
        # --- ESTE BLOQUE DEBE ESTAR ACTIVO ---
        try:
            if not self.es_client.indices.exists(index=self.es_index):
                with open(self.es_mapping_path) as f:
                    mapping_body = json.load(f)
                
                mappings_data = mapping_body.get('mappings')
                
                if mappings_data:
                    self.es_client.indices.create(index=self.es_index, mappings=mappings_data)
                    spider.log(f"Created new index '{self.es_index}' with custom mapping.")
                else:
                    spider.log("ERROR: 'mappings' not found in JSON file.", level=logging.ERROR)
                    
        except FileNotFoundError:
            spider.log(f"ERROR: Mapping file '{self.es_mapping_path}' not found.", level=logging.ERROR)
        except Exception as e:
            spider.log(f"ERROR during index creation: {e}", level=logging.ERROR)
            raise e

    def process_item(self, item, spider):
        doc = dict(item)
        doc_id = item['url'] # Usamos la URL como ID único (evita duplicados)
        
        try:
            self.es_client.index(index=self.es_index, id=doc_id, document=doc)
            spider.log(f"Indexed item: {item['title']}")
        except Exception as e:
            # Añadimos 'level=logging.ERROR' para registrar 
            # el error correctamente
            spider.log(f"ERROR during indexing: {e}", level=logging.ERROR) # <-- ✅ CORRECTO   
        return item