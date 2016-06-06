# -*- coding: utf-8 -*-



from core.exception import ProductError
from core.core import Core
from core.helpers.yaml_literal import Literal
from core.env_manager import EnvManager
from core.helpers.version import compare_versions
from core.download_manager import DownloadManager
from core.log_manager import LogManager
from core.models.platform import Platform
from core.models.file import File
from core.models.installer import Installer
from core.models.installed_product import InstalledProductInfo


import os
from collections import Iterable
from collections import OrderedDict






class BaseProduct(object):
    """
    Represent abstract class for product.
    Descendants: Product, Application, Engine.
    """

    def get_typename(self):
        """
        Descendant return string with type name: 'product', 'application' or 'engine'.
        This type name used in yaml represenstion for product:
        - product: Product1
          title: ...
        """
        raise NotImplementedError()

    def __init__(self, core: Core, attrs=None ):

        self.data = {}

        # internal
        self.core = core
        # self.envs  do nothing
        self.envs = EnvManager()
        self.installer = None
        # next fields are loaded from yaml
        # meta
        self.name = None
        self.title = None
        self.description = None
        self.link = None
        self.author = None
        self.icon = None
        # string list
        self.tags = []
        self.eula = None

        # fiters
        self.os = None
        self.bitness = None
        self.web_server = None
        self.lang = None
        self.platform = None

        # versions
        self.version = ''
        self.installed_version = ''

        # installer stuff
        self.dependencies = []
        self.files = []
        self.install_command = None
        self.upgrade_command = None
        self.config = None
        self.uninstall_command = None
        self.find_installed_command = None
        self.parameters = {}

        if attrs is not None:
            for item in attrs.keys():
                self.__dict__[item] = attrs[item]

            self.name = attrs[self.get_typename()]

            if attrs.get('files'):
                # create File objects for every file item
                self.files = []
                for f in attrs.get('files', []):
                    if f.get('file'):
                        self.files.append(File(self, **f))

            self.installer = Installer(self, self.install_command, self.upgrade_command,
                                        self.uninstall_command, self.find_installed_command)


    def merge(self, **kwargs):
        """
        Merges product representation in 'kwargs' dict with current product.
        Current product fields are overwritten by values from kwargs.
        :param kwargs: dict with product representation to merge.
        """
        # name of attribute (product, engine, application) with product name
        typename = self.get_typename()
        self.name = kwargs[typename]

        ####
        self.title = kwargs.get('title') or self.title
        self.description = kwargs.get('description') or self.description
        self.link = kwargs.get('link') or self.link
        self.author = kwargs.get('author') or self.author
        self.icon = kwargs.get('icon') or self.icon
        self.tags = kwargs.get('tags') or self.tags
        self.eula = kwargs.get('eula') or self.eula

        self.os = kwargs.get('os') or self.os
        self.bitness = kwargs.get('bitness') or self.bitness
        self.web_server = kwargs.get('webserver') or self.web_server
        self.lang = kwargs.get('lang') or self.lang

        # это поле не читается из ямла, оно создаётся из:
        self.platform = Platform(self.os, self.bitness, self.web_server, self.lang)

        self.dependencies = kwargs.get('dependencies', []) or self.dependencies

        self.version = str(kwargs.get('version', '')) or self.version
        self.installed_version = str(kwargs.get('installed_version', '')) or self.installed_version
        self.config = kwargs.get('config') or self.config

        files_list = kwargs.get('files', [])
        if files_list and len(files_list)>0:
            # create File objects for every file item
            self.files = []
            for f in files_list:
                fs = f.__getstate__() if isinstance(f, File) else f
                if fs.get('file'):
                    self.files.append(File(self, **fs))

        self.install_command = kwargs.get('install_command', None) or self.install_command
        if self.install_command:
            self.install_command = self.install_command.rstrip()

        self.upgrade_command = kwargs.get('upgrade_command', None) or self.upgrade_command
        if self.upgrade_command:
            self.upgrade_command = self.upgrade_command.rstrip()

        self.uninstall_command = kwargs.get('uninstall_command', None) or self.uninstall_command
        if self.uninstall_command:
            self.uninstall_command = self.uninstall_command.rstrip()

        self.find_installed_command = kwargs.get('find_installed_command', None) or self.find_installed_command
        if self.find_installed_command:
            self.find_installed_command = self.find_installed_command.rstrip()

        self.parameters = kwargs.get('parameters', None) or self.parameters
        # TODO must be deprecated
        # create Installer from commands,
        # installer knows to how call install_command, uninstall_command
        self.installer = Installer(self, self.install_command,
                                   self.upgrade_command,
                                   self.uninstall_command,
                                   self.find_installed_command)

    def __setattr__(self, name, value):
        self.__dict__[name] = value


    def __getstate__(self):
        """
        Returns ProductState object used in Yaml dumper.
        ProductState is smart OrderedDict wrapper.
        Method saves only non empty fields.
        :rtype : ProductState
        """
        result = ProductState()
        result[self.get_typename()] = self.name



        if self.title:
            result['title'] = self.title
        if self.description:
            result['description'] = Literal(self.description)
        if self.link:
            result['link'] = self.link
        if self.author:
            result['author'] = self.author
        if self.icon:
            result['icon'] = self.icon
        if self.tags:
            result['tags'] = self.tags
        if self.eula:
            result['eula'] = self.eula
        if self.os:
            result['os'] = self.os
        if self.bitness:
            result['bitness'] = self.bitness
        if self.web_server:
            result['web_server'] = self.web_server
        if self.lang:
            result['lang'] = self.lang
        if self.version:
            result['version'] = self.version

        result['installed_version'] = self.get_installed_version()

        if self.dependencies:
            result['dependencies'] = self.dependencies
        if self.files:
            result['files'] = [file.__getstate__() for file in self.files]
        if self.install_command:
            result['install_command'] = Literal(self.install_command)
        if self.upgrade_command:
            result['upgrade_command'] = Literal(self.upgrade_command)
        if self.uninstall_command:
            result['uninstall_command'] = Literal(self.uninstall_command)
        if self.find_installed_command:
            result['find_installed_command'] = Literal(self.find_installed_command)

        result['parameters'] = self.parameters or []
        if self.config:
            result["config"] = self.config
        return result

    def to_dict(self, rich=False)-> OrderedDict:
        """
        Dump product fields to OrderedDict used in JSON responses.
        :param rich: dump additional calculated fields.
        """
        product_dict = self.__getstate__().get_dict()
        if rich:
            product_dict['name'] = self.name
            product_dict['has_upgrade'] = self.has_upgrade()
            product_dict['is_upgradable'] = self.is_upgradable()
        return product_dict

    def __repr__(self):
        return '{0}({1}, {2})'.format(self.__class__.__name__, self.name, self.version or None)

    def is_installed(self)-> bool:
        """
        Check that great or equal version installed.
        Used in DependencyManager and self.install method.
        """
        if not self.installed_version:
            self.get_installed_version()
        if self.installed_version:
            compare_result = compare_versions(self.version, self.installed_version)
            return compare_result <= 0
        return False

    def is_installed_any_version(self):
        """
        Check that any version of product is installed.
        Used in DependencyManager and self.upgrade method.
        """
        if not self.installed_version:
            self.get_installed_version()
        return bool(self.installed_version)

    def install(self, parameters: dict)-> bool:
        """
        Installs itself:
        Skip installation if product is installed.
        Download files if they are not in cache yet.
        Call installer object with parameters.
        :param parameters: dict with parameters for installation, example: {'install_dir': 'c:\...'}
        :return: whether the installation was successful
        """
        if self.is_installed():
            return False
        # set name for log filename
        self.set_log_path('install')
        self.download()
        result = self.installer.install(parameters)
        self.unset_log_path('install')
        # logging.info("i have finished installing produxt {0}".format( str(result) ) )
        return result

    def upgrade(self, parameters: dict)-> bool:
        """
        Upgrades itself:
        Works like install(), but call 'upgrade' methid of installer.
        Download files if they are not in cache yet.
        Call installer object with parameters.
        :param parameters:
        :return: whether the upgrade was successful
        """
        # set name for lof filename
        self.set_log_path('upgrade')
        self.download()
        result = self.installer.upgrade(parameters)
        self.unset_log_path('upgrade')
        return result

    def uninstall(self):
        """
        Uninstalls itself.
        :return: whether the uninstallation was successful
        """
        self.set_log_path('uninstall')
        result = self.installer.uninstall()
        self.unset_log_path('uninstall')
        return result

    def find_installed(self)-> InstalledProductInfo:
        """
        Check whether itself is installed by calling find_installed_command.
        """
        result = None
        try:
            result = self.installer.find_installed()
            if result is not None:
                # remove trailing / from the end of
                if result.install_dir and (result.install_dir.startswith('/') or result.install_dir.endswith('\\')):
                    result.install_dir = result.install_dir[:-1]
        except Exception as e:
            raise ProductError("Product {0} find installed command failed ".format(self.name))

        return result

    def get_installed_version(self):
        """
        Searches and returns installed version in current products collection, see Core.current.
        """
        if not self.installed_version:
            # search in current by name if installed_version is empty
            synced_product = self.core.current_storage.feed.get_product(self.name)
            if synced_product:
                # save version if we are found itself in current
                self.installed_version = synced_product.installed_version
        return self.installed_version

    def get_dependencies(self)-> list:
        """
        Returns list of dependencies (product names)
        """
        return self.dependencies or []

    def download(self):
        """
        Downloads files for installation with DownloadManager.
        """
        if self.files:
            downloader = DownloadManager(self.core, self)
            downloader.download(self.files)


    # DEPRECATED
    def set_log_path(self, action: str):
        """
        Sets env variables with log paths. Used in installer.
        :param action: name of current action: 'install', 'uninstall', etc.
        """
        # self.envs['%{0}_LOG_PATH%'.format(action.upper())] = \
        #     LogManager.get_instance(self.core).get_log_path(action)

        # self.envs['%{0}_LOG_DIR%'.format(action.upper())] = \
        #     LogManager.get_instance(self.core).get_log_dir()
        pass

    # DEPRECATED
    def unset_log_path(self, action):
        """
        Removes env variables with log path. Called after installation.
        :param action: name of current action: 'install', 'uninstall', etc.
        """
        pass
        # del self.envs['%{0}_LOG_DIR%'.format(action.upper())]

    def has_search_tokens(self, *tokens)-> bool:
        """
        Checks that product attributes has at least one token from tokens list.
        Used in product search.
        :param tokens: list of string token to search: ['php', 'mysql']
        """
        for token in tokens:
            if not self.has_search_token(token):
                return False
        return True

    def has_search_token(self, token: str)-> bool:
        """
        Checks that search token are in product name, title, description, link or tags.
        Used in product search.
        :param token:
        """
        token = token.strip().lower()
        # search token in:
        # product.name
        if self.name.lower().find(token) >= 0:
            return True
        # product.title
        if self.title.lower().find(token) >= 0:
            return True
        # product.description
        if self.description and self.description.lower().find(token) >= 0:
            return True
        # product.link
        if self.link and self.link.lower().find(token) >= 0:
            return True
        # product.tags
        if self.tags:
            for tag in self.tags:
                if tag.lower().find(token) >= 0:
                    return True
        return False

    def has_upgrade(self)-> bool:
        """
        Checks that installed version is less then product version.
        This used as product attribute in templates for web ui.
        """
        # get installed version
        installed_version = self.get_installed_version()
        if installed_version:
            # compare installed and own version
            if compare_versions(self.version, installed_version) > 0:
                return True
        return False

    def is_upgradable(self)-> bool:
        """
        Check that product can be upgraded.
        This used as product attribute in templates for web ui.
        """
        return bool(self.upgrade_command)

    def get_product_with_version(self)-> str:
        """
        Returns product name with version formatted as 'Product==1.2.3.4'.
        Used in DependencyManager and ProductCollection.
        """
        return "{0}=={1}".format(self.name, self.version)


class ProductState(Iterable):
    """
    Represents product state as OrderedDict.
    Used for serialization to json and yaml.
    """
    def __init__(self):
        self._coll = OrderedDict()

    def __iter__(self):
        # iterator
        for k, v in self._coll.items():
            yield k, v

    def __setitem__(self, key, value):
        """
        Special method to implement 'ps[key] = value' syntax.
        """
        self._coll.__setitem__(key, value)

    def get_dict(self)-> OrderedDict:
        """
        Returns result as OrderedDict
        """
        return self._coll

