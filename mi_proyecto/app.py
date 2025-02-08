from flask import Flask, request, jsonify
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import json
from flask_cors import CORS
import subprocess
from fastapi import FastAPI, Query  # Asegúrate de importar Query

app = Flask(__name__)
CORS(app)  # Permite que el frontend Angular acceda a la API


@app.route('/movies', methods=['GET'])
def get_movies():
    try:
        # Después de que el scraper termine, lee el archivo de resultados
        with open('datos.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            return jsonify(data), 200
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({"error": "No data found"}), 404

# Ruta para ejecutar Scrapy
@app.get("/run_verpeliculasultra")
def run_verpeliculasultra():
    try:
        # Ejecuta Scrapy y guarda el JSON
        #subprocess.run(["scrapy", "crawl", "mi_spider"], check=True)
        subprocess.run(["scrapy", "crawl", "verpeliculasultra"], check=True)
        #return {"message": "Spider ejecutado correctamente"}
        with open("mi_proyecto/results/verpeliculasultra.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except Exception as e:
        return {"error": str(e)}

@app.get("/run_pelicinehd")
def run_pelicinehd():
    try:
        # Ejecuta Scrapy y guarda el JSON
        subprocess.run(["scrapy", "crawl", "pelicinehd"], check=True)
        #return {"message": "Spider ejecutado correctamente"}
        with open("mi_proyecto/results/pelicinehd.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except Exception as e:
        return {"error": str(e)}


@app.route("/get_verpeliculasultra", methods=["GET"])
def get_verpeliculasultra():

    search = request.args.get("search")
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    response = load_and_paginate_data("mi_proyecto/results/verpeliculasultra.json", search, page, per_page)
    return jsonify(response)

def load_and_paginate_data(file_path, search=None, page=1, per_page=10):
    """
    Carga un archivo JSON, filtra los datos si se proporciona un término de búsqueda y aplica paginación.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Filtrado por búsqueda
        if search:
            search = search.lower()
            data = [item for item in data if search in item.get("title", "").lower()]

        # Cálculo de los índices para la paginación
        start = (page - 1) * per_page
        end = start + per_page
        paginated_data = data[start:end]

        # Construcción de la respuesta JSON con paginación
        return {
            "page": page,
            "per_page": per_page,
            "total": len(data),
            "total_pages": (len(data) // per_page) + (1 if len(data) % per_page > 0 else 0),
            "data": paginated_data
        }
    except Exception as e:
        return {"error": str(e)}

@app.route("/get_pelicinehd", methods=["GET"])
def get_pelicinehd():
    search = request.args.get("search")
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    response = load_and_paginate_data("mi_proyecto/results/pelicinehd.json", search, page, per_page)
    return jsonify(response)      
@app.get("/run_pccomponentes")
def run_pccomponentes():
    try:
        # Ejecuta Scrapy y guarda el JSON
        subprocess.run(["scrapy", "crawl", "pccomponentes"], check=True)
        #return {"message": "Spider ejecutado correctamente"}
        with open("mi_proyecto/results/pccomponentes.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except Exception as e:
        return {"error": str(e)}
@app.route("/get_pccomponentes", methods=["GET"])
def get_pccomponentes():
    search = request.args.get("search")
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    response = load_and_paginate_data("mi_proyecto/results/pccomponentes.json", search, page, per_page)
    return jsonify(response)      

@app.get("/run_cinecalidad")
def run_cinecalidad():
    try:
        # Ejecuta Scrapy y guarda el JSON
        subprocess.run(["scrapy", "crawl", "cinecalidad"], check=True)
        #return {"message": "Spider ejecutado correctamente"}
        with open("mi_proyecto/results/cinecalidad.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except Exception as e:
        return {"error": str(e)}
@app.route("/get_cinecalidad", methods=["GET"])
def get_cinecalidad():
    search = request.args.get("search")
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    response = load_and_paginate_data("mi_proyecto/results/cinecalidad.json", search, page, per_page)
    return jsonify(response)      

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)