from flask import Flask, request, jsonify
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import json
from flask_cors import CORS
import subprocess
from fastapi import FastAPI, Query  # Asegúrate de importar Query
import random

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


@app.route("/get_products", methods=["GET"])
def get_products():
    try:
        # Fusionar productos de pccomponentes y wipoid
        all_products = merge_products("mi_proyecto/results/pccomponentes/portatiles-gaming.json", "mi_proyecto/results/wipoid/ordenadores-ordenadores-portatiles.json")

        # Obtener parámetros de búsqueda y paginación de la solicitud
        search = request.args.get("search")
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=10, type=int)

        # Paginar los productos fusionados
        response = load_and_paginate_data2(all_products, search, page, per_page)

        return jsonify(response)

    except Exception as e:
        return {"error": str(e)}

# Función para cargar y fusionar los productos de los archivos JSON
# Función para cargar y alternar los productos de los dos archivos JSON
def merge_products(pccomponentes_file, wipoid_file):
    try:
        # Cargar datos de ambos archivos JSON
        with open(pccomponentes_file, "r", encoding="utf-8") as file1:
            pccomponentes_data = json.load(file1)

        with open(wipoid_file, "r", encoding="utf-8") as file2:
            wipoid_data = json.load(file2)

        # Alternar los productos de pccomponentes y wipoid
        merged_products = []
        min_len = min(len(pccomponentes_data), len(wipoid_data))

        # Alternar entre ambos, asegurando que se muestre uno de cada ecommerce
        for i in range(min_len):
            merged_products.append(pccomponentes_data[i])
            merged_products.append(wipoid_data[i])

        # Si hay productos sobrantes de alguno de los dos, los añadimos
        merged_products.extend(pccomponentes_data[min_len:])
        merged_products.extend(wipoid_data[min_len:])
        
        return merged_products
    except Exception as e:
        return {"error": str(e)}


# Función para paginar los datos
def load_and_paginate_data2(data, search, page, per_page, order='asc'):
    # Filtrado por búsqueda (si es necesario)
    if search:
        search = search.lower()
        data = [item for item in data if search in item.get("title", "").lower()]

    # Paginación
    start = (page - 1) * per_page
    end = start + per_page
    
    paginated_data = data[start:end]
    # (Opcional) Filtrar los productos si es necesario, por ejemplo, por precio
    paginated_data = sorted(paginated_data, key=lambda x: float(x['price']
                                            .replace('€', '')  # Eliminar el símbolo de euro
                                            .replace('.', '')   # Eliminar los puntos (miles)
                                            .replace(',', '.')  # Reemplazar la coma por un punto decimal
                                            ), reverse=(order == 'desc')  # Si 'desc' se pasa, ordena de forma descendente
                )
    return {
        "total": len(data),
        "page": page,
        "per_page": per_page,
        "total_pages": (len(data) // per_page) + (1 if len(data) % per_page > 0 else 0),
        "data": paginated_data
    }       
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)