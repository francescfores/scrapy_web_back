import scrapy
import json
import random
from scrapy_playwright.page import PageMethod
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async  # ✅ Stealth corregido
from pathlib import Path

class MiSpider2(scrapy.Spider):
    name = 'wipoid_category'
    start_urls = ['https://wipoid.com/']
    current_page = 1

    custom_settings = {
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": False,
            "args": ["--disable-blink-features=AutomationControlled"],
        },
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9",
            "Referer": "https://www.google.com/",
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.movie_data = []
        self.movie_name = kwargs.get('movie_name', '')
        self.category = kwargs.get('category', '')
        self.subcategory = kwargs.get('subcategory', '')
        self.supercategory = kwargs.get('supercategory', '')

    def start_requests(self):
        for url in self.start_urls:
            if self.movie_name:
                url = f"https://wipoid.com/search/?query={self.movie_name}"
            elif self.supercategory:
                url = f"https://wipoid.com/{self.category}/{self.subcategory}/{self.supercategory}"
            elif self.subcategory:
                url = f"https://wipoid.com/{self.category}/{self.subcategory}"
            elif self.category:
                url = f"https://wipoid.com/{self.category}"
                
            yield scrapy.Request(
                url,
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
                    "playwright_page_methods": [
                        PageMethod(self.apply_stealth),
                        PageMethod(self.scroll_down),  # ✅ Aplica scroll
                    ],
                },
                callback=self.parse
            )

    async def apply_stealth(self, page):
        """Aplica Stealth para evadir detección."""
        await stealth_async(page)

    async def scroll_down(self, page):
        """Hace scroll hasta el final de la página simulando un usuario real."""
        last_height = await page.evaluate("document.body.scrollHeight")
        
        while True:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            await page.wait_for_timeout(random.randint(800, 1500))  # ✅ Espera aleatoria

            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:  # Si no cambia la altura, termina
                break
            last_height = new_height

# Aquí estamos asegurándonos de que el bloque de código que asigna `pages` 
# se ejecute solo después de obtener la respuesta del servidor.
# El siguiente código está indentado correctamente en el bloque correspondiente

    async def parse(self, response):
        playwright_page = response.meta["playwright_page"]
        pages = None
        # Obtener los productos
        productos = response.css('div.leo-product-ajax div.ajax_block_product')
        print(f"🔹 Página {self.current_page}: {len(productos)} productos encontrados.")

        for producto in productos:
            title = producto.css('h3.product-title a::text').get()
            link = producto.css('a::attr(href)').get()
            img = producto.css('img::attr(src)').get()
            price = producto.css('span.price::text').get()
            if link:
                self.movie_data.append({
                    "title": title,
                    "link": link,
                    "img": img,
                    "price": price,
                })

        # Definir pages al principio para evitar problemas con la indentación
            pages = response.css('button[aria-label="Página siguiente"]::attr(aria-label)').get()

        # Imprimir el valor de 'pages' para depuración
        # Comprobar si el botón "Página siguiente" está visible
        button = await playwright_page.query_selector('a.next')
        is_visible = await button.is_visible() if button else False

        self.current_page += 1
        
        if self.supercategory:
            next_page_url = f"https://wipoid.com/{self.category}/{self.subcategory}/{self.supercategory}/?page={self.current_page}"
        elif self.subcategory:
            next_page_url = f"https://wipoid.com/{self.category}/{self.subcategory}/?page={self.current_page}"
        elif self.category:
            next_page_url = f"https://wipoid.com/{self.category}/?page={self.current_page}"
        # Verificar si se encontró el botón "Página siguiente"
        if is_visible:  # Si 'pages' no es None (es decir, el botón existe)
            yield scrapy.Request(
                    next_page_url,
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
                        "playwright_page_methods": [
                            PageMethod(self.apply_stealth),
                            PageMethod(self.scroll_down),  # Aplica scroll
                        ],
                    },
                    callback=self.parse
                )
        else:
            # Si 'pages' es None, significa que el botón no existe
            print("No se encontró el botón 'Página siguiente'. No hay más páginas.")
        
        await playwright_page.close()

    def closed(self, reason):
        #directorio = Path(f"mi_proyecto/results/wipoid/{self.category}")
        directorio = Path(f"mi_proyecto/results/wipoid")
        directorio.mkdir(parents=True, exist_ok=True)  # `exist_ok=True` evita errores si ya existe
        print(f"Directorio '{directorio}' creado o ya existente.")

        if self.supercategory:
            with open(f"mi_proyecto/results/wipoid/{self.category}-{self.subcategory}-{self.supercategory}.json", "w", encoding="utf-8") as f:
                json.dump(self.movie_data, f, ensure_ascii=False, indent=4)
        elif self.subcategory:
            with open(f"mi_proyecto/results/wipoid/{self.category}-{self.subcategory}.json", "w", encoding="utf-8") as f:
                json.dump(self.movie_data, f, ensure_ascii=False, indent=4)
        elif self.category:
            with open(f"mi_proyecto/results/wipoid/{self.category}.json", "w", encoding="utf-8") as f:
                json.dump(self.movie_data, f, ensure_ascii=False, indent=4)