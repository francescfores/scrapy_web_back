from flask import Flask, jsonify
import requests
from flask_cors import CORS
import subprocess
import json
app = Flask(__name__)
CORS(app)  # Permite que el frontend Angular acceda a la API

SCRAPYRT_URL = 'http://localhost:9080'

@app.route('/scrape', methods=['GET'])
def scrape():
    # Hace una solicitud a scrapyrt para ejecutar el spider MiSpider2
    response = requests.get(f'{SCRAPYRT_URL}/crawl.json', params={'spider_name': 'mi_spider_pelishd'})
    
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({"error": "Failed to scrape data"}), response.status_code

@app.route('/scrape2', methods=['GET'])
def scrape2():
    # Hace una solicitud a scrapyrt para ejecutar el spider MiSpider
    response = requests.get(f'{SCRAPYRT_URL}/crawl.json', params={'spider_name': 'mi_spider'})
    
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({"error": "Failed to scrape data"}), response.status_code

@app.route('/movies', methods=['GET'])
def get_movies():
    try:
        # Hace una solicitud a scrapyrt para obtener los datos
        response = requests.get(f'{SCRAPYRT_URL}/crawl.json', params={'spider_name': 'mi_spider'})
        
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "No data found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para ejecutar Scrapy
@app.get("/run_mi_spider")
def run_mi_spider():
    try:
        # Ejecuta Scrapy y guarda el JSON
        subprocess.run(["scrapy", "crawl", "mi_spider", "-o", "mi_spider.json"], check=True)
        #return {"message": "Spider ejecutado correctamente"}
        with open("mi_proyecto/results/mi_spider.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except Exception as e:
        return {"error": str(e)}

@app.get("/run_mi_spider_pelishd")
def run_mi_spider_pelishd():
    try:
        # Ejecuta Scrapy y guarda el JSON
        subprocess.run(["scrapy", "crawl", "mi_spider_pelishd", "-o", "mi_spider_pelishd.json"], check=True)
        #return {"message": "Spider ejecutado correctamente"}
        with open("mi_proyecto/results/mi_spider_pelishd.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except Exception as e:
        return {"error": str(e)}

# Ruta para obtener los datos del JSON
@app.get("/get_mi_spider")
def get_mi_spider():
    try:
        with open("mi_proyecto/results/mi_spider.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except Exception as e:
        return {"error": str(e)}

# Ruta para obtener los datos del JSON
@app.get("/get_mi_spider_pelishd")
def get_mi_spider_pelishd():
    try:
        with open("mi_proyecto/results/mi_spider_pelishd.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except Exception as e:
        return {"error": str(e)}  

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)