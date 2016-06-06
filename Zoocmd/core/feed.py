# -*- coding: utf-8 -*-


from .version_comparer import ProductComparer
from .feed_loader import FeedLoader
from .helpers.version import compare_versions
from .models.base_product import BaseProduct
from core.exception import ProductNotFoundError
from .models.product import Product
from .models.application import Application
from .models.engine import Engine
from .models.platform import Platform


import logging

class Feed(object):
    """
    Внутреннее представление загруженного ямла (или нескольких ямлов).
    Умеет загружать ямлы.
    Хранит внутри кусочки продуктов, которые написаны в ямле.
    Умеет искать по этим кусочкам, делать и мержить из них продукты.
    """

    _instance = None

    def __init__(self, core, platform):
        self.core = core
        self.platform = platform
        # сырая внутрення коллекция кусочков продуктов из ямлов
        self.raw_collection = []
        #  урлы из которых загружать ямлы
        self.urls = []

    def __repr__(self):
        return 'Feed(platform={0}, len(items)={1}, urls={2})'.format(self.platform.__repr__(),
                                                                     len(self.raw_collection),
                                                                     self.urls
                                                                     )

    def iter(self):
        """
        Хелпер-Итератор по внутренней коллекции,
        """
        for i in self.raw_collection:
            yield i

    def get(self):
        """
        Возвращает сырую внутреннюю коллекцию.
        """
        return self.raw_collection

    def clear(self):
        """
        Очищает внутреннюю коллекцию.
        """
        self.raw_collection.clear()

    def load(self, *urls):
        """
        Загружает ямлы.
        :param urls: список урлов для заргузки.
        """
        self.urls = urls
        # объект-загрузчик
        feed_loader = FeedLoader(self.core, *self.urls)
        self._internal_load(feed_loader)

    def _internal_load(self, feed_loader: FeedLoader):
        """
        внутренний загрузчик ямлов.
        """
        self.raw_collection = []
        # загрузить
        items = feed_loader.load()
        # добавить в коллекцию
        self.raw_collection.extend(items)


    def add_raw_item(self, item: dict):
        """
        Добавить во внутреннюю коллекцию кусочек ямла.
        """
        self.raw_collection.append(item)

    def add_raw_list(self, items: list):
        """
        Добавить во внутреннюю коллекцию список кусочков ямлов.
        """
        self.raw_collection.extend(items)

    def update(self):
        """
        Перезагрузить ямлы.
        """
        logging.debug('updating feed: {0}'.format(self.urls))
        feed_loader = FeedLoader(self.core, *self.urls)
        self._internal_load(feed_loader)

    @staticmethod
    def get_main_name(**data):
        """
        Возвращает типа продукта из кусочка ямла.
        По этому типу создаётся нужный класс продукта: Product, Engine, Application.
        """
        if 'application' in data:
            return 'application'
        if 'engine' in data:
            return 'engine'
        if 'product' in data:
            return 'product'

    def get_products(self):
        """
        Создаёт и возвращает список продуктов из сырых данных.
        """
        # временный словарь ядл хранения продуктов по имени
        products = {}
        # цикл по сырой коллекции
        for data in self.iter():
            # data - сырой кусочек ямла в виде dict
            # проверим, совпала ли платформа (ос, версия, битность, вебсервер)
            if self._match_platform(**data):
                # платформа совпала
                # получим тип продукта
                product_type = self.get_main_name(**data)
                # получим имя продукта
                name = data[product_type]
                # получим продукт из временной коллекции, может быть нул
                product = products.get(name, None)
                # примержим (или создадим) к продукту кусочек ямла
                product_merged = self._create_or_merge_product(product, **data)
                # сохраним новый продукт во временной коллекции
                products[name] = product_merged


        # отсортируем продукты во временной коллекции по имени и вернём списком
        return sorted(products.values(), key=lambda k: k.name)

    def _match_platform(self, **data)-> bool:
        """
        Сравнивает текущую платформу с той, что в кусочке ямла.
        """
        platform = Platform.from_product_dict(**data)
        return self.platform.match(platform)

    @staticmethod
    def _match_product_and_version(product_name_version, **data)-> bool:
        """
        Сравнивает имя и версию продукта в строке с теми, что есть в кусочке ямла
        :param product_name_version: строка вида "product==1.0" или просто "product"
        :param data: кусочек ямла
        """
        pc = ProductComparer(product_name_version)
        return pc.match(data[Feed.get_main_name(**data)], str(data.get('version', '')))

    def _create_or_merge_product(self, original_product: BaseProduct, **data)-> BaseProduct:
        """
        Мержит продукт с кусочком ямла
        или
        создаёт продукт из кусочка ямла.
        :param original_product: продукт, может пуст, тогда его создадут
        :param data: кусочек ямла
        """
        if original_product:
            # продукт уже есть
            if not original_product.version:
                # у продукта пока нет версии  - мержим
                original_product.merge(**data)
            else:
                # у продукта уже есть версия (была смержена раньше)
                if data.get('version'):
                    # в кусочке ямла тоже есть версия
                    if compare_versions(str(data.get('version')), original_product.version) >= 0:
                        # мержим только если в ямле версия равна или больше, чем у продукта
                        original_product.merge(**data)
                else:
                    # в кусочке ямла нет версии - мержим
                    original_product.merge(**data)
        else:
            # продукта еще нет, создадим его
            original_product = self.create_product(**data)
            # примержим к вновь созданному продукту сырой кусочек ямла
            original_product.merge(**data)

        # вернём продукт
        return original_product

    def create_product(self, **data):
        """
        Создаёт и возвращает продукт из сырого кусочка ямла.
        """
        # тип продукта
        main_name = self.get_main_name(**data)
        # создаём продукт соответствующего типа
        if "application" == main_name:
            return Application(self.core)
        if "engine" == main_name:
            return Engine(self.core)
        if "product" == main_name:
            return Product(self.core)

    def get_product_or_exception(self, product_name_version: str):
        """
        Ищет и возвращает продукт по имени, если не найден - ошибка
        """
        p = self.get_product(product_name_version)
        if not p:
            raise ProductNotFoundError('Product {0} not found'.format(product_name_version))
        return p

    # TODO save product class to yaml

    def get_product(self, product_name_version: str) -> BaseProduct:
        """
        Создаёт (мержит) и возвращает продукт по имени.
        :param product_name_version: имя и версия продукта в виде "product==1.1" или просто "product"
        """
        # объект который умеет сравнивать имена с версиями
        pc = ProductComparer(product_name_version)

        result_product = None
        # цикл по сырым кусочкам ямла
        for data in self.iter():
            # кусочек ямла совпал с текущей платформой?
            if self._match_platform(**data):
                # да, создаём временный продукт
                product = self.create_product(**data)
                product.merge(**data)
                # если его имя и версия совпрали с заданным
                if pc.match(product.name, product.version):
                    # то примержим в продукту-результату
                    if result_product:
                        result_product = self._create_or_merge_product(result_product, **data)
                    else:
                        # а если результата еще нет, то просто определим его
                        result_product = product

        # если есть продукт результат и него есть версия (т.е. это не абстрактный продукт)
        if result_product and result_product.version:
            # вернём его
            return result_product

        return None

    # def get_product_versions(self, product_name):
    #     versions = []
    #     for data in self.iter():
    #         if self._match_product_and_version(product_name, **data):
    #             if self._match_platform(**data):
    #                 version = data.get('version')
    #                 if version:
    #                     version = str(version).lower()
    #                     if not version in versions:
    #                         versions.append(version)
    #     return versions

    def remove_product(self, product_name):
        """
        Удаляет из сырой коллекции все кусочки ямла у которых имя product_name.
        В итоге — удаление продукта из коллекции.
        """
        self.raw_collection = [data for data in self.raw_collection if data[self.get_main_name(**data)] != product_name]

    def update_product(self, product: BaseProduct):
        """
        Удаляет из сырой коллекции продукт и добавляет новое сырое представление продукта.
        :param product: продукт, который нужно добавить в коллекцию
        """
        self.remove_product(product.name)
        self.raw_collection.append(product.to_dict())

    def has_product(self, name, version)-> bool:
        """
        Возвращает, есть ли продукт с именем name и версией version в сырой коллекции.
        """
        # цикл по сырой коллекции
        for data in self.iter():
            # сравниваем имя
            if data[self.get_main_name(**data)] == name:
                # а если есть версия — то и версию
                if version:
                    if version == data.get('version'):
                        return True
                else:
                    return True
        return False

    @staticmethod
    def get_tags(products: list)-> list:
        """
        Возвращает список тэгов (категорий) и их количество для списка продуктов, используется в морде.
        Результат в ткой виде:
        - db: 3
        - cms: 4
        - all: 7
        """
        raw_tags = {}
        all_count = 0
        # цикл по продуктам
        for product in products:
            # если у продукта есть теги
            if product.tags:
                all_count += 1
                # цикл по тегам
                for tag in product.tags:
                    # запомним тег
                    if tag in raw_tags:
                        raw_tags[tag] += 1
                    else:
                        raw_tags[tag] = 1
        raw_tags['all'] = all_count

        # сконверитруем в список
        tags = [{'name': name, 'count': count} for name, count in raw_tags.items()]
        # и отсортируем
        tags = sorted(tags, key=lambda k: k['name'])

        return tags

    @staticmethod
    def dump_products(products):
        """
        Сериализует списолк продуктов в список словарей.
        Дальше используется для сериализации в yaml или json.
        """
        result = []
        for product in products:
            product_dict = product.to_dict(rich=True)
            result.append(product_dict)

        return result

    def filter_products(self, product_filter=None, installed=None):
        """
        Фильтрует продукты по типу: product, engine или application
        :param product_filter: фильтр
        :param installed: оставлять только установленные
        """
        for product in self.get_products():
            if product_filter:
                # check type is product, application or engine
                if product.get_typename() != product_filter:
                    continue
            if installed is not None:
                if product.is_installed() != bool(installed):
                    continue
            if isinstance(product, Engine):
                # если это энжин и он установлен - обновим его конфиг из engines.yaml
                if product.is_installed():
                    product.update_config()
            yield product

    def search_products(self, q=None)->list:
        """
        Ищет продукты.
        Возвращает список продуктов, в внтури которого (имя, описание, теги) есть слово 'q'
        """
        q = q or ''
        tokens = q.split(' ')
        return [product for product in self.get_products() if product.has_search_tokens(*tokens)]
