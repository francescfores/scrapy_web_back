import scrapy
import json

class MiSpider2(scrapy.Spider):
    name = 'cinecalidad2'
    start_urls = ['https://cinecalidad2s.ec/']

    def __init__(self, *args, **kwargs):
        super(MiSpider2, self).__init__(*args, **kwargs)
        self.saved_html = False
        self.movie_data = []
        self.movie_name = kwargs.get('movie_name', '')
        self.category = kwargs.get('category', '')

    def start_requests(self):
        for url in self.start_urls:
            if self.movie_name:
                url = f"https://cinecalidad2s.ec/?s={self.movie_name}"
            if self.category:
                url = f"https://cinecalidad2s.ec/{self.category}"

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

    def parse(self, response):
        productos = response.css('div.custom')
        if not self.movie_name or not self.category:
            productos=productos[4:]

        counter = 0
        for producto in productos:
            if counter >= 2:  # Solo procesar hasta el tercer producto
                break
            counter += 1 
            title = producto.css('a::attr(title)').get()
            link = producto.css('a::attr(href)').get()
            img = producto.css('img::attr(src)').get()
            print(f"title: {title}")
            print(f"link: {link}")
            print(f"img: {img}")

            if img and img.startswith('/'):
                img = 'https://cinecalidad.com' + img

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

        # Verifica si 'playwright_page' está presente
        playwright_page = response.meta.get("playwright_page")
        
        if not playwright_page:
            self.logger.error("❌ No se pudo encontrar 'playwright_page' en response.meta")
            return

        try:
            # Asegurarse de que el elemento está presente antes de hacer click
            await playwright_page.evaluate('document.querySelector("div.bs-message").remove()')
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
            self.logger.error(f"🚨 Error al interactuar con la página: {e}")

        # Cerrar la página de Playwright después de usarla
        await playwright_page.close()

    def closed(self, reason):
        try:
            with open('mi_proyecto/results/cinecalidad.json', 'w', encoding='utf-8') as f:
                json.dump(self.movie_data, f, ensure_ascii=False, indent=4)
            print("Datos guardados correctamente en 'mi_proyecto/results/cinecalidad.json'")
        except Exception as e:
            print(f"Error al guardar el archivo JSON: {e}")
