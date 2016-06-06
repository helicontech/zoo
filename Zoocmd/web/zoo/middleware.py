# -*- coding: utf-8 -*-


class StaticFilesCachingMiddleware:
    """
    Прослойка для джанго-приложения, которая
    ставит кеширующие хидеры для статики
    и запрещает кеширование для html-документов.
    """

    ACCEPTABLE_CONTENT_TYPES = (
        'application/javascript',
        'text/css',
        'image/png',
        'image/gif',
    )

    def process_response(self, request, response):
        # получим типа ответа
        content_type = response.get('Content-Type')
        # если это статика или шрифт
        if content_type and content_type in self.ACCEPTABLE_CONTENT_TYPES or 'webfont' in request.path:
            # закешируем на час
            response['Cache-Control'] = 'public,max-age=3600'
            response['X-Zoo-Static'] = '1'
        if content_type and 'text/html' in content_type:
            # если это html-документ — запрещаем кешировать
            response['Cache-Control'] = 'no-cache,no-store,must-revalidate,max-age=0'

        return response

