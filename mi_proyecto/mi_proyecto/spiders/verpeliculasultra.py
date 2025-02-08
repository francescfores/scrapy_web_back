import scrapy
import json

class MiSpider2(scrapy.Spider):
    name = 'verpeliculasultra'
    start_urls = ['https://verpeliculasultra.com/']

    def __init__(self, *args, **kwargs):
        super(MiSpider2, self).__init__(*args, **kwargs)
        self.saved_html = False
        self.movie_data = []

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True ,
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
        with open('mi_proyecto/results/verpeliculasultra.json', 'w') as f:
            f.truncate(0)
        return spider

    async def parse(self, response):
        productos = response.css('div.shortf')
        web_title = response.css('title::text').get()
        print(f"web_title: {web_title}")

        counter = 0
        for producto in productos:
            if counter >= 2:  # Solo procesar hasta el tercer producto
                break
            counter += 1 

            title = producto.css('a::attr(title)').get()
            link = producto.css('a::attr(href)').get()
            img = producto.css('img::attr(src)').get()
            if img.startswith('/'):
                img = 'https://verpeliculasultra.com' + img

            if link:
                yield response.follow(
                    link,
                    callback=self.parse_movie,
                    meta={
                        "playwright": True ,
                    'playwright_context': 'new',
                    "playwright_include_page": True,
                    "playwright_context_kwargs": {
                        "java_script_enabled": False,
                        "ignore_https_errors": True,
                    },  
                    "playwright_page_goto_kwargs": {
                        "wait_until": "domcontentloaded",
                    },
                    'title': title,  'link': link, 'img': img}
                )
            


    async def parse_movie(self, response):
        print(f"response.meta: {response.meta}")  # Depuración

        playwright_page = response.meta.get("playwright_page")  # Obtener la página de Playwright

        if not playwright_page:
            self.logger.error("❌ No se pudo encontrar 'playwright_page' en response.meta")
            return

        try:
            #obtener todas las opciones dentro de tabs-sidebar-ul ay un li con a se tiene que hacer click
            options = response.css('ul.tabs-sidebar-ul li a::attr(href)').getall()
            for option in options:
                print(":🔗 options", option , end="\n\n")
                await playwright_page.evaluate('document.querySelector("ul.tabs-sidebar-ul li a").click()')
                print("🎬 Esperando play-btn...")
            
            await playwright_page.wait_for_selector("div.play-btn", timeout=10000)
            # Hacer clic en todos los botones "play-btn"
            await playwright_page.evaluate('document.querySelectorAll("div.play-btn").forEach(btn => btn.click());')
            # Esperar que el iframe cargue y obtener su src
            await playwright_page.wait_for_selector("iframe", timeout=10000)
            # Obtener todas las URLs de los iframes
            iframe_urls = await playwright_page.evaluate('''
                Array.from(document.querySelectorAll("iframe")).map(iframe => iframe.src);
            ''')

            #iframe_url = await playwright_page.eval_on_selector_all("iframe", "iframes => iframes.map(iframe => iframe.src)")

            print(f"✅ URL del iframe: {iframe_urls}")

            # Guardar información de la película
            self.movie_data.append({
                "title": response.meta.get("title"),
                "link": response.meta.get("link"),
                "img": response.meta.get("img"),
                "movie_link": iframe_urls
            })
        except Exception as e:
            self.logger.error(f"🚨 Error al hacer clic en el play-btn: {e}")

        # Cerrar la página de Playwright después de usarla
        await playwright_page.close()

    def closed(self, reason):
        try:
            with open('mi_proyecto/results/verpeliculasultra.json', 'w', encoding='utf-8') as f:
                json.dump(self.movie_data, f, ensure_ascii=False, indent=4)
            print("Datos guardados correctamente en 'mi_proyecto/results/verpeliculasultra.json'")
        except Exception as e:
            print(f"Error al guardar el archivo JSON: {e}")
