import scrapy
import json

class MiSpider2(scrapy.Spider):
    name = 'cinecalidad'
    start_urls = ['https://cinecalidad2.ec/']
    current_page = 1  # Empezamos desde la página 1

    def __init__(self, *args, **kwargs):
        super(MiSpider2, self).__init__(*args, **kwargs)
        self.saved_html = False
        self.movie_data = []

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    'playwright_context': 'new',
                    "playwright_include_page": True,
                    "playwright_context_kwargs": {
                        "java_script_enabled": True,
                        "ignore_https_errors": True,
                    },
                    "playwright_page_goto_kwargs": {
                        "wait_until": "domcontentloaded",
                        "timeout": 30*1000,
                    },
                },
                callback=self.parse
            )

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(MiSpider2, cls).from_crawler(crawler, *args, **kwargs)
        with open('mi_proyecto/results/cinecalidad.json', 'w') as f:
            f.truncate(0)
        return spider

    async def parse(self, response):
        playwright_page = response.meta.get("playwright_page")
        await playwright_page.evaluate('document.querySelector("div.bs-message").remove()')

        productos = response.css('div.custom')
        web_title = response.css('title::text').get()
        print(f"web_title: {web_title}")

        counter = 0
        for producto in productos[4:]:  # Omitir los primeros 3 elementos
            """ if counter >= 6:  # Solo procesar 3 elementos después de omitir los primeros 3
                break
            counter += 1  """

            title = producto.css('div.in_title::text').get()
            link = producto.css('a::attr(href)').get()
            img = producto.css('img::attr(src)').get()

            if img and img.startswith('/'):
                img = 'https://verpeliculasultra.com' + img

            if link:
                yield response.follow(
                    link,
                    callback=self.parse_movie,
                    meta={
                        'playwright': True,
                        'playwright_context': 'new',
                        'playwright_include_page': True,
                        'playwright_context_kwargs': {
                            'java_script_enabled': False,
                            'ignore_https_errors': True,
                        },
                        'playwright_page_goto_kwargs': {
                            'wait_until': 'domcontentloaded',
                        },
                        'title': title,
                        'link': link,
                        'img': img
                    }
                )

        # A continuación, si hay más páginas, haz la solicitud para la siguiente
        self.current_page += 1
        next_page_url = f'https://www.cinecalidad.ec/page/{self.current_page}/'
        print(f"🔗 Navegando a la siguiente página: {next_page_url}")

        if self.current_page <= 10:  # Limitar la cantidad de páginas
            yield scrapy.Request(
                next_page_url,
                meta=response.meta,
                callback=self.parse
            )

    async def parse_movie(self, response):
        playwright_page = response.meta.get("playwright_page")
        await playwright_page.evaluate('document.querySelector("div.bs-message").remove()')

        if not playwright_page:
            self.logger.error("❌ No se pudo encontrar 'playwright_page' en response.meta")
            return

        try:
            await playwright_page.wait_for_selector("li#player-option-1", timeout=10000)
            await playwright_page.evaluate('document.querySelector("li#player-option-1").click()')
            await playwright_page.wait_for_selector("iframe", timeout=10000)
            iframe_urls = await playwright_page.evaluate('''
                Array.from(document.querySelectorAll("iframe")).map(iframe => iframe.src);
            ''')

            self.movie_data.append({
                "title": response.meta.get("title"),
                "link": response.meta.get("link"),
                "img": response.css('img.alignnone::attr(src)').get(),
                "movie_link": iframe_urls[1:]
            })
        except Exception as e:
            self.logger.error(f"🚨 Error al hacer clic en el play-btn: {e}")

        # Cerrar la página de Playwright después de usarla
        await playwright_page.close()

    def closed(self, reason):
        try:
            with open('mi_proyecto/results/cinecalidad.json', 'w', encoding='utf-8') as f:
                json.dump(self.movie_data, f, ensure_ascii=False, indent=4)
            print("Datos guardados correctamente en 'mi_proyecto/results/cinecalidad.json'")
        except Exception as e:
            print(f"Error al guardar el archivo JSON: {e}")
