# Define aquí los modelos para tu middleware de spider
#
# Consulta la documentación en:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# útil para manejar diferentes tipos de items con una sola interfaz
from itemadapter import ItemAdapter


class WeworkremotelySpiderMiddleware:
    # No es necesario definir todos los métodos. Si un método no está definido,
    # scrapy actúa como si el middleware del spider no modificara los
    # objetos pasados.

    @classmethod
    def from_crawler(cls, crawler):
        # Este método es utilizado por Scrapy para crear tus spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Llamado para cada respuesta que pasa por el middleware del spider
        # y entra al spider.

        # Debe devolver None o lanzar una excepción.
        return None

    def process_spider_output(self, response, result, spider):
        # Llamado con los resultados devueltos por el Spider, después de
        # que ha procesado la respuesta.

        # Debe devolver un iterable de objetos Request o item.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Llamado cuando un spider o el método process_spider_input()
        # (de otro middleware de spider) lanza una excepción.

        # Debe devolver None o un iterable de objetos Request o item.
        pass

    async def process_start(self, start):
        # Llamado con un iterador asíncrono sobre el método start() del spider o el
        # método coincidente de un middleware de spider anterior.
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class WeworkremotelyDownloaderMiddleware:
    # No es necesario definir todos los métodos. Si un método no está definido,
    # scrapy actúa como si el middleware de descarga no modificara los
    # objetos pasados.

    @classmethod
    def from_crawler(cls, crawler):
        # Este método es utilizado por Scrapy para crear tus spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Llamado para cada solicitud que pasa por el middleware
        # de descarga.

        # Debe:
        # - devolver None: continuar procesando esta solicitud
        # - o devolver un objeto Response
        # - o devolver un objeto Request
        # - o lanzar IgnoreRequest: se llamarán los métodos process_exception()
        #   del middleware de descarga instalado
        return None

    def process_response(self, request, response, spider):
        # Llamado con la respuesta devuelta por el descargador.

        # Debe:
        # - devolver un objeto Response
        # - devolver un objeto Request
        # - o lanzar IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Llamado cuando un gestor de descargas o un process_request()
        # (de otro middleware de descarga) lanza una excepción.

        # Debe:
        # - devolver None: continuar procesando esta excepción
        # - devolver un objeto Response: detiene la cadena process_exception()
        # - devolver un objeto Request: detiene la cadena process_exception()
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
