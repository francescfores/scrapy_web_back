import scrapy 
import json
from scrapy_splash import SplashRequest

class MiSpider(scrapy.Spider):
    name = 'pelicinehd'
    start_urls = ['https://www.pelicinehd.com/peliculas',]
    current_page = 1  # Empezamos desde la página 1

    def __init__(self, *args, **kwargs):
        super(MiSpider, self).__init__(*args, **kwargs)
        self.saved_html = False  # Flag para asegurarnos de guardar solo una vez
        self.movie_data = []  # Lista para acumular los datos de las películas

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={'wait': 2})

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(MiSpider, cls).from_crawler(crawler, *args, **kwargs)
        # Vaciar el archivo antes de comenzar la araña
        with open('mi_proyecto/results/pelicinehd.json', 'w') as f:
            f.truncate(0)  # Limpiar el contenido del archivo
        return spider

    def parse(self, response):
        productos = response.css('li.movies')
        web_title = response.css('title::text').get()
        print(f"web_title: {web_title}")
        counter = 0
        
        # Extraemos los enlaces de las películas
        for producto in productos:
           

            link = producto.css('a::attr(href)').get()
            img = producto.css('img::attr(src)').get()
            if img and img.startswith('/'):
                img = 'https:' + img
            if link:
                yield response.follow(link, callback=self.parse_movie, meta={'img': img})
        
                # A continuación, si hay más páginas, haz la solicitud para la siguiente
        self.current_page += 1
        next_page_url = f'https://www.pelicinehd.com/peliculas/page/{self.current_page}/'
        print(f"🔗 Navegando a la siguiente página: {next_page_url}")

        if self.current_page <= 10:  # Limitar la cantidad de páginas
            yield scrapy.Request(
                next_page_url,
                meta=response.meta,
                callback=self.parse
            )
    def parse_movie(self, response):
        img = response.meta.get('img')  # Obtenemos la imagen del `meta`
        title = response.css('h1::text').get()

        movie_link = response.css('iframe::attr(data-src)').getall()

        # Imprimir los datos para ver qué estamos extrayendo
        print(f"Título: {title}")
        print(f"Enlaces: {movie_link}")

        # Acumulamos los datos en la lista
        self.movie_data.append({
            'title': title,
            'img': img,
            'movie_link': movie_link
        })


    def closed(self, reason):
        # Este método se ejecuta al finalizar el spider
        try:
            # Escribimos todos los datos acumulados en el archivo JSON
            with open('mi_proyecto/results/pelicinehd.json', 'w', encoding='utf-8') as f:
                json.dump(self.movie_data, f, ensure_ascii=False, indent=4)  # Escribir toda la lista en el archivo JSON

            print("Datos guardados correctamente en 'mi_proyecto/results/pelicinehd.json'")
        except Exception as e:
            print(f"Error al guardar el archivo JSON: {e}")
