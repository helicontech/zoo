
class DependencyException(Exception):
    def __init__(self,  message, product):
        super(Exception, self).__init__(message)
        self.message = message
        self.product = product
        self.do_not_print = True




class SelfUpgradeException(Exception):
        def __init__(self, message, parent_pid):
            super(Exception, self).__init__(message)
            self.message = message
            self.parent_pid = parent_pid


class TaskException(Exception):
        def __init__(self,  message, product, tb):
            super(Exception, self).__init__(message)
            self.message = message
            self.product = product
            self.traceback = tb


class ProductNotFoundError(Exception):
    pass


class FeedLoaderDownload(Exception):
    pass

class ProductError(Exception):
    pass