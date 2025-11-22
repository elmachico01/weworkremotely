import scrapy
from ..items import JobItem
from datetime import datetime

class WeworkSpider(scrapy.Spider):
    name = 'wework'
    allowed_domains = ['weworkremotely.com']
    start_urls = ['https://weworkremotely.com/remote-jobs/search'] 

    def parse(self, response):
        
        # 1. Extrae los enlaces de los trabajos de la página actual (como antes)
        job_links = response.css(
            'li.new-listing-container:not(.feature--ad) > a::attr(href)'
        ).getall()
        self.log(f"Found {len(job_links)} job links on: {response.url}")
        
        for link in job_links:
            yield response.follow(link, self.parse_job_detail)

        # --- 2. LÓGICA AÑADIDA ---
        # Encuentra todos los enlaces "View all..." (basado en image_62a4b0.png)
        # y ordénalos para evitar seguir el mismo enlace varias veces si aparece
        # en diferentes secciones (aunque los duplicados ya se gestionan)
        view_all_links = sorted(list(set(response.css('li.view-all > a::attr(href)').getall())))
        
        if view_all_links:
            self.log(f"Found {len(view_all_links)} 'View all' links to follow.")
            for link in view_all_links:
                # Sigue el enlace a la página de la categoría (ej. /categories/...)
                # y llama a este mismo método 'parse' en esa página
                # para extraer los trabajos.
                yield response.follow(link, self.parse)
        # -------------------------

    def parse_job_detail(self, response):
        """
        --- MÉTODO ACTUALIZADO ---
        Usa los selectores específicos de las capturas de pantalla para title, company
        y añade company_description.
        """
        
        item = JobItem()
        item['url'] = response.url
        item['scrape_timestamp'] = datetime.utcnow().isoformat()
        
        # --- SELECTORES CSS ACTUALIZADOS (de tus capturas de pantalla) ---
        
        # Título 
        item['title'] = response.css(
            'h1.lis-container__header__hero__company-info__title::text'
        ).get("").strip()
        
        # Empresa 
        item['company'] = response.css(
            'div.lis-container__job__sidebar__companyDetails__info__title > h3::text'
        ).get("").strip()

        # Descripción de la empresa 
        desc_texts = response.css(
            'div.lis-container__header__hero__company-info__description ::text'
        ).getall()
        # Unimos todos los textos limpios
        item['company_description'] = ' '.join(text.strip() for text in desc_texts if text.strip())
        
        item['logo_url'] = response.css(
            'div.lis-container__header__hero__company-logo::attr(style)'
        ).get("").strip()
        # ---------------------------------------------------

        # Descripción del trabajo (sin cambios)
        item['description'] = response.css('div.lis-container__job__content__description').get()

        # --- SELECTORES SIDEBAR XPath (sin cambios) ---
        
        item['posted_date'] = response.xpath(
            "//li[contains(., 'Posted on')]/span/text()"
        ).get("").strip()
        
        item['job_type'] = response.xpath(
            "//li[contains(., 'Job type')]//span[contains(@class, 'box--jobType')]/text()"
        ).get("").strip()
        
        item['category'] = response.xpath(
            "//li[contains(., 'Category')]//span[contains(@class, 'box--blue')]/text()"
        ).get("").strip()

        # --- SELECTOR AÑADIDO PARA EL SALARIO ---
        # Usa la misma lógica de la categoría, pero busca 'Salary'
        item['salary'] = response.xpath(
            "//li[contains(., 'Salary')]//span[contains(@class, 'box--blue')]/text()"
        ).get("").strip()
        # ----------------------------------------
        
        # 1. Extrae la lista "sucia"
        countries_list = response.xpath(
            "//li[contains(., 'Country')]//span[contains(@class, 'box--multi')]/text()"
        ).getall()
        
        # 2. Limpia la lista: aplica strip() a cada elemento y elimina los vacíos
        item['country'] = [c.strip() for c in countries_list if c.strip()]
        # ---------------------------
        
        yield item