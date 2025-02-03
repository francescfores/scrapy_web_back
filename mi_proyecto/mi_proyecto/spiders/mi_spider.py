import scrapy 
import json
from scrapy_splash import SplashRequest

class MiSpider(scrapy.Spider):
    name = 'mi_spider'
    start_urls = ['https://www.pelicinehd.com',]

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
        with open('mi_proyecto/results/mi_spider.json', 'w') as f:
            f.truncate(0)  # Limpiar el contenido del archivo
        return spider

    def parse(self, response):
        productos = response.css('li.movies')
        web_title = response.css('title::text').get()
        print(f"web_title: {web_title}")
        counter = 0
        
        # Extraemos los enlaces de las películas
        for producto in productos:
            if counter >= 2:  # Solo procesar hasta el tercer producto
                break
            counter += 1

            link = producto.css('a::attr(href)').get()
            img = producto.css('img::attr(src)').get()
            if link:
                yield response.follow(link, callback=self.parse_movie, meta={'img': img})

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

        # Si aún no hemos guardado el HTML, lo hacemos ahora
        if not self.saved_html:
            with open('response_content.html', 'w', encoding='utf-8') as f:
                f.write(response.text)  # Guardamos el contenido de la respuesta en un archivo
            self.saved_html = True

        yield {
            'title': title,
            'img': img,
            'movie_link': movie_link
        }

    def closed(self, reason):
        # Este método se ejecuta al finalizar el spider
        try:
            # Escribimos todos los datos acumulados en el archivo JSON
            with open('mi_proyecto/results/mi_spider.json', 'w', encoding='utf-8') as f:
                json.dump(self.movie_data, f, ensure_ascii=False, indent=4)  # Escribir toda la lista en el archivo JSON

            print("Datos guardados correctamente en 'mi_proyecto/results/mi_spider.json'")
        except Exception as e:
            print(f"Error al guardar el archivo JSON: {e}")
