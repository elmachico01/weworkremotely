import os
from flask import Flask, render_template, request, jsonify
from elasticsearch import Elasticsearch

# --- Configuración ---
app = Flask(__name__) 

try:
    es = Elasticsearch("http://localhost:9200")
    if not es.ping():
        raise ValueError("Error: Unable to connect to Elasticsearch.")
    print("Connected to Elasticsearch.")
except Exception as e:
    print(f"Fatal error: {e}")
    es = None

ES_INDEX = "wework_jobs_final"


# --- Ruta 1: La "carcasa" de nuestra App ---
@app.route('/')
def home():
    return render_template('index.html')


# --- Ruta 2: Nuestra API (LÓGICA MULTI-SELECT) ---
@app.route('/api/search')
def api_search():
    """
    Search API with FACETED SEARCH and MULTI-SELECT logic.
    """
    if not es:
        return jsonify({"error": "Elasticsearch is not connected"}), 500

    # 1. Recopilar las entradas (ahora como LISTAS)
    query_text = request.args.get('q', '')
    filters = {
        "category": request.args.getlist('category'), # <-- .getlist()
        "country": request.args.getlist('country'),   # <-- .getlist()
        "job_type": request.args.getlist('job_type'), # <-- .getlist()
        "salary": request.args.getlist('salary'),     # <-- .getlist()
        "skill": request.args.getlist('skill')        # <-- .getlist()
    }

    # 2. Construir la consulta de búsqueda de texto
    must_clause = {"match_all": {}}
    if query_text:
        must_clause = {
            "multi_match": {
                "query": query_text,
                "fields": ["title^3", "skills^2", "description", "company", "category"]
            }
        }

    # 3. Construir la lista de todos los filtros ACTIVOS
    active_filters = []
    filter_fields = {
        "category": "category",
        "country": "country",
        "job_type": "job_type",
        "salary": "salary",
        "skill": "skills" # Campo 'skills' en ES
    }
    
    for key, values in filters.items():
        if values: # Si la lista no está vacía
            field_name = filter_fields[key]
            active_filters.append({"terms": {field_name: values}}) # <-- consulta 'terms' (plural)

    # 4. Construir la consulta principal para los RESULTADOS (hits)
    main_query = {
        "bool": {
            "must": must_clause,
            "filter": active_filters
        }
    }

    # 5. Construir las AGREGACIONES (faceted)
    aggs_body = {}
    
    for key, field_name in filter_fields.items():
        # Excluir el filtro actual de la lista de filtros para calcular los contadores correctamente
        other_filters = [f for f in active_filters if field_name not in f.get("terms", {})] # <-- verificar 'terms'
        
        agg_filters_list = [must_clause] + other_filters
        
        bucket_size = 1000 if key == "skills" else 100
        
        aggs_body[f"all_{field_name}"] = {
            "filter": {
                "bool": {
                    "must": agg_filters_list
                }
            },
            "aggs": {
                "buckets": {
                    "terms": {
                        "field": field_name, 
                        "size": bucket_size  
                    }
                }
            }
        }

    # 6. Construir la consulta completa
    search_body = {
        "size": 100,
        "query": main_query,
        "aggs": aggs_body,
        "highlight": {
            "fields": {"description": {}}
        }
    }

    # 7. Ejecutar la consulta
    try:
        response = es.search(index=ES_INDEX, body=search_body)
        
        # 8. Preparar la respuesta JSON (sin cambios en la estructura)
        results = {
            "hits": response['hits']['hits'],
            "total": response['hits']['total']['value'],
            "categories": response['aggregations']['all_category']['buckets'],
            "countries": response['aggregations']['all_country']['buckets'],
            "job_types": response['aggregations']['all_job_type']['buckets'],
            "salaries": response['aggregations']['all_salary']['buckets'],
            "skills": response['aggregations']['all_skills']['buckets']
        }
        return jsonify(results)

    except Exception as e:
        print(f"Error during search: {e}")
        return jsonify({"error": str(e)}), 500

# --- Inicio del Servidor ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)