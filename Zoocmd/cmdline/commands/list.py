# -*- coding: utf-8 -*-


class ListProductsCommand(object):
    """
    Wrapper class to print product list
    """

    def __init__(self, feed):
        self.feed = feed

    @staticmethod
    def print(table):
        """
        print product table
        :param table: list of lists with colums to print
        :return:
        """
        col_widths = [max(len(x) for x in col) for col in zip(*table)]
        for line in table:
            result = "| " + " | ".join(u"{0:{1}}".format(x, col_widths[i] or 1) for i, x in enumerate(line)) + " |"
            print(result)

    def products(self, install_dir=False):
        """
        print all products from feed
        :param install_dir: whether to display the install directory
        """
        table = []
        products = self.feed.get_products()
        for product in products:
            row = (
                product.name,
                product.version,
                product.get_installed_version() or "-"
            )
            if install_dir:
                row += (product.parameters.get('install_dir') or '-',)
            table.append(row)

        self.print(table)

    def installed(self):
        """
        print installed product from feed
        """
        table = []
        for product in self.feed.get_products():
            if product.is_installed_any_version():
                table.append(
                    (product.name,
                     product.version,
                     product.get_installed_version() or "-")
                )

        self.print(table)

    def search(self, q):
        """
        search products by 'q' term and print it
        :param q: search term
        """
        words = q.split(' ')
        words = [w.strip().lower() for w in words]
        table = []
        for product in self.feed.get_products():
            for word in words:
                if product.name.lower().find(word) >= 0 or product.title.lower().find(
                        word) >= 0 or product.description.lower().find(word) >= 0:
                    table.append(
                        (product.name,
                         product.version,
                         product.get_installed_version() or "-")
                    )
                    break
        self.print(table)
