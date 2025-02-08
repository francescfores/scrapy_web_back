# Crear el entorno virtual (en la carpeta actual)
python3 -m venv venv

# En macOS/Linux:
source venv/bin/activate

# Instalar Scrapy dentro del entorno virtual
pip install scrapy

# Crear el proyecto Scrapy
scrapy startproject mi_proyecto

# You can start your first spider with:
cd mi_proyecto
scrapy genspider example example.com

# Crear el proyecto Scrapy
touch app.py

pip install scrapy_splash
pip install flask
pip install flask_cors
pip install fastapi

# Ejecutar scrawl manualmente

cd mi_proyecto/mi_proyecto
scrapy crawl mi_spider 


pip install scrapy-playwright
playwright install

run api
cd mi_proyecto/
python app.py

scrapy crawl cinecalidad2 -a movie_name="Sonic"
