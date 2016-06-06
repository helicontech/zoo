# -*- coding: utf-8 -*-

import logging
import sys
import os
import re
import yaml
import pythoncom
import win32com.client
from collections import OrderedDict
import core.core
from core.core import Core
from core.helpers.urls import combine_virtual_path, remove_starting_backward_slash
from core.helpers.yaml_helper import YamlHelper
from core.helpers.zoo_config import get_zoo_config
from core.models.site import Site, SiteApplication, SiteVirtialDirectory
from core.models.application import Application
from core.models.app_pool import AppPool
from core.parameters_manager import KnownParameters
from core.helpers.yaml_literal import Literal
from .base import BaseWebServer
from core.helpers.common import expand_variables_in_dict, expand_zoo_variables

class IIS(BaseWebServer):
    """
    IIS web server API.
    """
    # TODO IT MUST BE ADJUSTED FROM SETTINGS
    APP_CMD = r'C:\Windows\System32\inetsrv\appcmd.exe'
    APP_CMD_EXPRESS_PATH = r'C:\Program Files\IIS Express\iisexpress.exe'
    APP_CMD_EXPRESS = r'C:\Program Files\IIS Express\appcmd.exe'
    # TODO REMOVE THIS HARDCODED VAR
    DEFAULT_WEBISTES_FOLDER = r'c:\inetpub'
    DEFAULT_WEBISTES_FOLDER_EXPRESS = r'%USERPROFILE%\Documents\My Web Sites'

    def __init__(self, core, is_express):
        self.is_express = is_express
        self.core = core
        if self.is_express:
            self.APP_CMD = self.APP_CMD_EXPRESS
            self.DEFAULT_WEBISTES_FOLDER = self.core.expandvars(self.DEFAULT_WEBISTES_FOLDER_EXPRESS)

    def get_server_node(self):
        return {
            'name': 'Microsoft IIS' if not self.is_express else 'Microsoft IIS Express',
            'path': '',
            'type': 'server'
        }

    @classmethod
    def is_installed(cls) -> bool:
        """
        Check IIS installed.
        """
        from core.api.windows.registry import Registry
        registry = Registry()
        major_version = registry.read("HKLM\\SOFTWARE\\Microsoft\\INETSTP", "MajorVersion")
        minor_version = registry.read("HKLM\\SOFTWARE\\Microsoft\\INETSTP", "MinorVersion")
        return bool(major_version)

    def create_physical_path_for_virtual_path(self, name):
        """
        Creates web site folder
        """
        path = os.path.join(self.DEFAULT_WEBISTES_FOLDER, name)
        self.core.api.os.shell.make_dir(path)
        return path

    def site_create_from_dict(self, parameters: dict):
        """
        Creates web site from parameters passed to installer.
        Example parameters:
        {
            "app-pool-name": "DefaultAppPool",
            "site-name": "test6006"
        }
        """
        site_name = parameters[KnownParameters.SITE_NAME.value]
        site_path = self.create_physical_path_for_virtual_path(site_name)
        bindings = parameters[KnownParameters.SITE_BINDING.value]
        # use default app pool by default
        pool = parameters.get(KnownParameters.POOL_NAME.value, None)

        self.site_create(site_name, site_path, bindings, pool)

    def launch_iis_express(self, site_name):
        """
        Launch an iisexpress deamon for the site
        "iisxexpress /site:sitename"
        """
        executable = IIS.APP_CMD_EXPRESS_PATH
        if not Core.exist_uniq_process("iisexpress_"+site_name):
            Core.start_uniq_process([executable, "/site:{0}".format(site_name)], "iisexpress_"+site_name)
        return True



    def get_available_port(self):
        sites = self.get_list_of_sites()
        possible_port = 4000
        busy_ports = {}
        for item in sites:
            busy_ports[item.port] = True
            if possible_port == item.port:
                possible_port += 1
                while possible_port in busy_ports:
                    possible_port += 1
        return possible_port

    def get_default_site_params(self, name="default"):
        if self.is_express:
            path4application = os.path.join(self.DEFAULT_WEBISTES_FOLDER, name)
            site_name = name
            i = 0
            while i < 100:

                if not os.path.exists(path4application):
                    parameters = {}
                    parameters[KnownParameters.CREATE_SITE.value] = True
                    parameters[KnownParameters.SITE_NAME.value] = site_name
                    """
                    bindings =
                    website.protocol + '/' +
                    website.ip_address + ':' +
                    website.port +':' +
                    website.hostname;
                    """
                    port = self.get_available_port()
                    parameters[KnownParameters.SITE_BINDING.value] = "http/*:{0}:localhost".format(port)
                    return parameters
                else:
                    site_name = "{0}_{1}".format(name, str(i))
                    path4application = os.path.join(self.DEFAULT_WEBISTES_FOLDER, site_name)
                    i += 1
        return {}




    def site_create(self, name, path, bindings, pool=None):
        """
        Creates web site using appcmd.exe utility
        # C:\Windows\System32\inetsrv\appcmd.exe add site
        # appcmd add site /name:"prova" bindings:http://localhost:8080 /physicalPath:c:\sites\prova
        # APPCMD.exe set app "prova/" /applicationPool:"<APP_POOL_NAME_HERE>"
        # http/*:85:marketing.contoso.com
        """

        os.makedirs(path, exist_ok=True)
        self.core.api.os.shell.cmd('{0} add site /name:"{1}" /physicalPath:"{2}" /bindings:{3}'.format(
            self.APP_CMD, name, path, bindings
        ))
        if pool:
            self.core.api.os.shell.cmd('{0} set app "{1}/" /applicationPool:"{2}"'.format(
                self.APP_CMD, name, pool
            ))

    def site_delete(self, name):
        """
        Deletes site using appcmd.exe utility
        """
        self.core.api.os.shell.cmd('{0} delete site "{1}"'.format(self.APP_CMD, name))

    def pool_create_from_dict(self, parameters: dict):
        """
        Creates app pool from paramters
        """
        pool_name = parameters[KnownParameters.SITE_NAME.value]
        parameters[KnownParameters.POOL_NAME.value] = pool_name
        for pool in self.get_app_pool_list():
            if pool.name.lower() == pool_name.lower():
                return
        return self.pool_create(pool_name)

    def pool_create(self, pool_name):
        """
        Creates app pool using appcmd.exe utility
        """
        self.core.api.os.shell.cmd('{0} add apppool /name:"{1}"'.format(
            self.APP_CMD, pool_name
        ))

    # create environment from config
    def create_environment(self, config: dict, std_env: dict, selected_engine=None):
        app = config['application']
        parameters = app['parameters']

        if selected_engine is None:
            selected_engine = parameters.get('selected-engine', None)

        temp_env = std_env
        if selected_engine:
            engine = self.core.engine_storage.get_product(selected_engine)
            if engine is not None:
                engine_config = engine.config
                if engine_config:
                    if 'environment_variables' in engine_config:
                        engine_env = engine_config.get('environment_variables', None)
                        new_engine_env = std_env
                        for keyi in engine_env:
                                temp_var = os.path.expandvars(engine_env[keyi])
                                new_engine_env[keyi] = expand_zoo_variables(new_engine_env, temp_var)
                            
                        temp_env.update(new_engine_env)

        logging.debug(temp_env)
        for item in app['engines']:
            if item['engine'] == selected_engine:
                if "environment_variables" in item:
                    env_vars_engine = item.get('environment_variables', None)
                    if env_vars_engine:
                        temp_engine_env = temp_env
                        for var in env_vars_engine:
                            # temp_var = os.path.expandvars(env_vars_engine[var])
                            temp_var = env_vars_engine[var]
                            temp_engine_env[var] = expand_zoo_variables(temp_env, temp_var)
                            temp_engine_env[var] = expand_zoo_variables(temp_engine_env, temp_engine_env[var])

                        temp_env.update(temp_engine_env)

        logging.debug(temp_env)
        return temp_env

    def application_create_from_dict(self, parameters: dict):
        """
        Creates web app from paramters
        """
        # check is exists
        if self.is_app_exists(parameters[KnownParameters.SITE_NAME.value], parameters[KnownParameters.APP_NAME.value]):
            return

        site_name = parameters[KnownParameters.SITE_NAME.value]
        app_virtual_path = parameters[KnownParameters.APP_NAME.value]
        physical_path = parameters.get(KnownParameters.PHYSICAL_PATH.value)
        if not physical_path:
            app_folder = app_virtual_path.replace('/', '\\')
            app_folder = remove_starting_backward_slash(app_folder)
            physical_path = self.create_physical_path_for_virtual_path(os.path.join(site_name, app_folder))

        # use default app pool by default
        pool = parameters.get(KnownParameters.POOL_NAME.value, None)
        self.app_create(site_name, app_virtual_path, physical_path, pool)

    def app_create(self, site_name, virt_path, phys_path, pool=None):
        """
        Creates web app using appcmd utility
        # appcmd add app /site.name: string /path: string /physicalPath: string
        """
        if virt_path[0] != '/':
            virt_path = '/' + virt_path
        self.core.api.os.shell.cmd('{0} add app /site.name:"{1}" /path:"{2}" /physicalPath:"{3}"'.format(
            self.APP_CMD, site_name, virt_path, phys_path
        ))
        if pool:
            self.core.api.os.shell.cmd('{0} set app "{1}" /applicationPool:"{2}"'.format(
                self.APP_CMD, site_name + virt_path, pool
            ))

    def siteroot4path(self, source_physical_path):
        list = self.core.api.os.web_server.get_webserver_list()
        # trick cause of sre_constants.error: bogus escape: '\\U'
        source_physical_path = source_physical_path.replace('\\', '/')
        physical_path = source_physical_path

        while True:
            path_re = re.compile(r'{0}'.format(physical_path), re.I)
            for site in list:
                if site["path"] == physical_path:
                    return site["path"]
            (physical_path, Head) = os.path.split(physical_path)


            if physical_path == self.DEFAULT_WEBISTES_FOLDER:
                return None

    def app_delete(self, name):
        """
        Deletes web app using appcmd.exe utility
        """
        self.core.api.os.shell.cmd('{0}  delete app /app.name:"{1}"'.format(self.APP_CMD, name))

    def find_app_physical_path(self, source_physical_path, site_root=None):
        list = self.core.api.os.web_server.get_webserver_list()
        # trick cause of sre_constants.error: bogus escape: '\\U'
        source_physical_path = source_physical_path.replace('\\', '/')
        path_list = [source_physical_path]
        physical_path = source_physical_path
        path_root_re = re.compile(r'{0}'.format(site_root), re.I)

        while True:
            zoo_physical_path = os.path.join(physical_path, '.zoo')
            if os.path.exists(zoo_physical_path):
                return physical_path

            if physical_path == site_root:
                break
            (physical_path, Head) = os.path.split(physical_path)

            if physical_path == "":
                break

        return None


    def get_webserver_list(self):
        output = self.core.api.os.shell.get_cmd_output('{0} list vdir'.format(self.APP_CMD))

        if output:
            result = []
            app_name_re = re.compile(r'VDIR\s+"([^"]+)"\s+\(physicalPath:(.+)\)', re.I)
            output = output.decode(sys.stdout.encoding)
            for line in output.splitlines(keepends=False):
                match = app_name_re.match(line)
                # trick cause of sre_constants.error: bogus escape: '\\U'
                physical_path = os.path.expandvars(match.group(2))
                physical_path = physical_path.replace('\\', '/')
                result.append({"site": match.group(1), "path": physical_path})
            return result
        else:
            return None

    def map_webserver_path(self, app_name)-> str:
        """
        Maps virtual path to physical path.
        :param app_name: virtual path
        :return: physical path
        """
        path = None
        if app_name == '':
            return None

        if app_name and not app_name.endswith('/'):
            app_name += '/'

        app_name_re = re.compile(r'VDIR\s+"{0}"\s+\(physicalPath:(.+)\)'.format(app_name), re.I|re.UNICODE)

        # list virtual directories and search app_name path
        # VDIR "test 6565/blog 1/" (physicalPath:c:\inetpub\test 6565\blog 1)
        output = self.core.api.os.shell.get_cmd_output('{0} list vdir'.format(self.APP_CMD))

        if output:
            output = output.decode(sys.stdout.encoding)
            for line in output.splitlines(keepends=False):
                match = app_name_re.match(line)
                if match:
                    path = match.group(1)
        if path:
            path = self.core.expandvars(path)
        else:
            app_name = app_name[:-1]
            (physical_path, head) = os.path.split(app_name)
            path = self.map_webserver_path(physical_path)
            if path:
                 return os.path.join(path, head)

        return path

    def get_iis_object(self):
        """
        Returns Microsoft.ApplicationHost.WritableAdminManager COM-object
        """
        pythoncom.CoInitialize()
        if self.is_express:
            # нельзя выносить это в отдельную фунцию, не работает магия
            # versionMgr, iisex, Microsoft.ApplicationHost.WritableAdminManager должны быть в одном scope
            iis_product_express = 2
            version_manager = win32com.client.dynamic.Dispatch("Microsoft.IIS.VersionManager")
            try:
                iisex = version_manager.GetVersionObject("8.0", iis_product_express)
            except:
                iisex = version_manager.GetVersionObject("7.5", iis_product_express)

            iisex.ApplyManifestContext()

        result = win32com.client.dynamic.Dispatch("Microsoft.ApplicationHost.WritableAdminManager")
        return result

    def get_list_of_sites(self) -> list:
        """
        Returns list of Site objects
        """
        ah_write = self.get_iis_object()
        section = ah_write.GetAdminSection("system.applicationHost/sites", "MACHINE/WEBROOT/APPHOST")
        collection = section.Collection
        result = []

        for i in range(collection.Count):

            site = collection[i]
            prop = site.Properties
            # site_id = prop["id"].Value
            name = prop["name"].Value
            default_app = self.get_default_app(site)
            bindings = self.get_site_bindings(site.ChildElements)
            applications = self.get_applications(site)
            if default_app and not os.path.exists(default_app["physicalPath"]):
                # не показывать сайты для которых нет физ. директории для иис экспреса
                continue
            site = Site(name, bindings, default_app, applications)
            result.append(site)

        return result

    def get_site(self, name) -> Site:
        """
        Return Site object by name
        """
        ah_write = self.get_iis_object()
        section = ah_write.GetAdminSection("system.applicationHost/sites", "MACHINE/WEBROOT/APPHOST")
        collection = section.Collection

        for i in range(collection.Count):
            site = collection[i]
            prop = site.Properties
            site_name = prop["name"].Value
            if site_name == name:
                #site_id = prop["id"].Value
                default_app = self.get_default_app(site)
                bindings = self.get_site_bindings(site.ChildElements)
                apps = self.get_applications(site)

                return Site(name, bindings, default_app, apps)

        return None

    @staticmethod
    def get_site_bindings(site_elements) -> list:
        """
        Returns list of site bindings
        :param site_elements: ChildElements attr of site COM-object
        """
        collection = site_elements["bindings"].Collection
        result = []
        for i in range(collection.Count):
            prop = collection[i].Properties
            protocol = prop["protocol"].Value
            binding_info = prop["bindingInformation"].Value
            result.append((protocol, binding_info))

        return result

    @staticmethod
    def get_default_app(site):
        """
        Returns dict with default app of site
        :param site: site COM-object
        """
        collection = site.Collection
        for i in range(collection.Count):
            prop = collection[i].Properties
            if prop["path"].Value == "/":
                result = dict()
                result["applicationPool"] = collection[i].Properties["applicationPool"].Value
                result["virtualPath"] = collection[i].Collection[0].Properties["path"].Value
                result["physicalPath"] = collection[i].Collection[0].Properties["physicalPath"].Value
                return result

        return None

    @staticmethod
    def get_applications(site) -> list:
        """
        Returns list of site apps
        :param site: site COM-object
        """
        collection = site.Collection
        result = []
        for i in range(collection.Count):
            prop = collection[i].Properties
            result.append(SiteApplication(
                prop["path"].Value,
                prop["applicationPool"].Value
            ))

        return result

    def is_app_exists(self, name, app_path) -> bool:
        """
        Check is app exists
        :param name: site name
        :param app_path: virtual path
        """
        ah_write = self.get_iis_object()
        section = ah_write.GetAdminSection("system.applicationHost/sites", "MACHINE/WEBROOT/APPHOST")
        collection = section.Collection

        for i in range(collection.Count):
            site = collection[i]
            prop = site.Properties
            site_name = prop["name"].Value
            if site_name != name:
                continue
            app_collection = site.Collection
            for ii in range(app_collection.Count):
                app_prop = app_collection[ii].Properties
                if remove_starting_backward_slash(app_prop["path"].Value) == remove_starting_backward_slash(app_path):
                    # found!
                    return True

        return False

    def get_app_virtual_directories(self, name, app_path) -> list:
        """
        Returns list of SiteVirtialDirectory objects for app
        :param name: site name
        :param app_path: virtual path
        """
        ah_write = self.get_iis_object()
        section = ah_write.GetAdminSection("system.applicationHost/sites", "MACHINE/WEBROOT/APPHOST")
        collection = section.Collection
        result = []

        app_path_for_vdir = ""
        if app_path != "/":
            app_path_for_vdir = app_path

        for i in range(collection.Count):
            site = collection[i]
            prop = site.Properties
            site_name = prop["name"].Value
            if site_name != name:
                continue

            app_collection = site.Collection
            for ii in range(app_collection.Count):
                app_prop = app_collection[ii].Properties
                app = app_collection[ii]
                if app_prop["path"].Value != app_path:
                    continue

                vdir_collection = app.Collection
                for iii in range(vdir_collection.Count):
                    vdir_prop = vdir_collection[iii].Properties

                    result.append(SiteVirtialDirectory(
                        app_path_for_vdir + vdir_prop["path"].Value,
                        vdir_prop["physicalPath"].Value
                    ))

        return result

    def get_app_pool_list(self) -> list:
        """
        Returns list of AppPool objects
        """
        ah_write = self.get_iis_object()
        section = ah_write.GetAdminSection("system.applicationHost/applicationPools", "MACHINE/WEBROOT/APPHOST")
        collection = section.Collection
        result = list()

        for i in range(collection.Count):
            site = collection[i]
            prop = site.Properties

            name = prop["name"].Value
            managed_runtime_version = prop["managedRuntimeVersion"].Value
            if prop["managedPipelineMode"].Value:
                managed_pipeline_mode = "classic"
            else:
                managed_pipeline_mode = "integrated"
            if prop["enable32BitAppOnWin64"].Value:
                bitness = 32
            else:
                bitness = 64

            result.append(AppPool(name, managed_runtime_version, managed_pipeline_mode, bitness))

        return result

    @staticmethod
    def create_zoo_config(physical_path, config: dict):
        """
        Saves zoo app config to .zoo file
        :param physical_path: path to app
        :param config: zoo app config as dict
        """
        logging.debug("physical_path='{0}', settings={1}".format(physical_path, config))
        physical_path = os.path.join(physical_path, '.zoo')
        if "description" in config:
            config["description"] = Literal(config["description"])

        if "find_installed_command" in config:
            config["find_installed_command"] = Literal(config["find_installed_command"])

        if "install_command" in config:
            config["install_command"] = Literal(config["install_command"])

        if "uninstall_command" in config:
            config["uninstall_command"] = Literal(config["uninstall_command"])

        if "upgrade_command" in config:
            config["upgrade_command"] = Literal(config["upgrade_command"])

        YamlHelper.save(config, physical_path)

    @staticmethod
    def get_zoo_config(physical_path) -> dict:
        """
        Loads and returns zoo app config from .zoo file in path
        :param physical_path: path to app
        """
        physical_path = os.path.join(physical_path, '.zoo')
        if os.path.exists(physical_path):
            with open(physical_path, 'r') as stream:
                config = yaml.load(stream)
                return config
        return None

    def update_zoo_config(self, site_name, virt_path, new_config):
        """
        Writes zoo app config to .zoo file
        if new_config is empty then just write empty .zoo file (parent app disabled)
        :param site_name: site name
        :param virt_path: virtual path
        :param new_config: zoo app config as dict
        """
        root_path = self.map_path(site_name, virt_path)
        zoo_config_path = os.path.join(root_path, ".zoo")
        config = get_zoo_config(zoo_config_path) or {}

        app = config.get('application')
        # disabled ability
        if 'selected-engine' in new_config :
            new_engine = new_config.get('selected-engine')
            if 'parameters' in app:
                app['parameters']['selected-engine'] = new_engine
            else:
                app['parameters'] = OrderedDict()
                app['parameters']['selected-engine'] = new_engine


        if 'engines' in new_config:
            engines = new_config.get('engines')
            app['engines'] = engines

        if 'locations' in new_config:
            app['locations'] = new_config['locations']

        if "description" in app:
            app["description"] = Literal(app["description"])

        if "find_installed_command" in app:
            app["find_installed_command"] = Literal(app["find_installed_command"])

        if "install_command" in app:
            app["install_command"] = Literal(app["install_command"])

        if "uninstall_command" in app:
            app["uninstall_command"] = Literal(app["uninstall_command"])

        if "upgrade_command" in app:
            app["upgrade_command"] = Literal(app["upgrade_command"])

        # save .zoo
        YamlHelper.save(config, zoo_config_path)

    def get_site_node(self, site_name):
        """
        Returns site node as dict for server tree
        """
        site = self.get_site(site_name)
        if site:
            physical_path = site.default_app["physicalPath"]
            zoo_config_path = os.path.join(physical_path, ".zoo")
            node = {
                "name": site_name,
                "path": combine_virtual_path(site_name, '/'),
                "physical_path": physical_path,
                "type": "site",
                "config": get_zoo_config(zoo_config_path),
                'bindings': site.bindings,
                'urls': site.urls
            }
        else:
            node = None
        return node

    def get_path_node(self, site_name, virtual_path):
        """
        Returns node of virtual path for server tree
        """
        vdirs = self.get_subvirtualdirectories(site_name, virtual_path)
        for v in vdirs:
            if v.path == virtual_path:
                physical_path = os.path.abspath(v.physical_path)
                name = os.path.basename(physical_path)
                zoo_config_path = os.path.join(physical_path, ".zoo")
                node = {
                    "name": name,
                    "path": combine_virtual_path(site_name, virtual_path),
                    "physical_path": physical_path,
                    "type": "virtual directory",
                    'is_virtual': True,
                    "config": get_zoo_config(zoo_config_path)
                }
                return node

        physical_path = os.path.abspath(self.map_path(site_name, virtual_path))
        name = os.path.basename(physical_path)
        zoo_config_path = os.path.join(physical_path, ".zoo")
        node = {
            "name": name,
            "path": combine_virtual_path(site_name, virtual_path),
            "physical_path": physical_path,
            "type": "directory",
            "config": get_zoo_config(zoo_config_path)
        }
        return node

    def get_directories(self, site_name, virt_path):
        """
        Returns list of dict with child physical directories of virtual path
        """
        logging.debug("site_name='{0}' virt_path='{1}'".format(site_name, virt_path))
        result = []

        if site_name is None and virt_path is None:
            # return list of sites
            core = Core.get_instance()
            sites = core.api.os.web_server.get_list_of_sites()
            for site in sites:
                # physical_path = self.map_path(site.name, "/")  # slow
                physical_path = site.default_app["physicalPath"]
                zoo_config_path = os.path.join(physical_path, ".zoo")
                result.append(
                    {
                        "name": site.name,
                        "path": site.name + '/',
                        "physical_path": physical_path,
                        "type": "site",
                        # "config": get_zoo_config(zoo_config_path),
                        "bindings": site.bindings,
                        'urls': site.urls
                    }
                )

        else:
            # check site exists
            test_site = self.get_site(site_name)
            if test_site:
                # site exists
                root_path = self.map_path(site_name, virt_path)
                sub_dirs = self.get_subdirectories(root_path)

                for d in sub_dirs:
                    physical_path = os.path.abspath(d)
                    name = os.path.basename(physical_path)
                    zoo_config_path = os.path.join(physical_path, ".zoo")
                    result.append(
                        {
                            "name": name,
                            "path": combine_virtual_path(site_name, combine_virtual_path(virt_path, name)),
                            "physical_path": physical_path,
                            "type": "directory",
                            "config": get_zoo_config(zoo_config_path)
                        }
                    )

                vdirs = self.get_subvirtualdirectories(site_name, virt_path)

                for vdir in vdirs:
                    physical_path = vdir.physical_path
                    name = os.path.basename(vdir.path[:-1])
                    zoo_config_path = os.path.join(physical_path, ".zoo")

                    self.remove_by_name(result, name)

                    result.append(
                        {
                            "name": name,
                            "path": combine_virtual_path(site_name, vdir.path),
                            "physical_path": physical_path,
                            "type": "virtual directory",
                            'is_virtual': True,
                            "config": get_zoo_config(zoo_config_path)
                        }
                    )
            else:
                # site not exists
                result = []

        result = sorted(result, key=lambda d: d["name"].lower())

        return result

    def map_path_get_site(self, sites_collection, site_name):
        """
        Helper to search site_name in sites_collection
        :return:
        """
        for i in range(sites_collection.Count):
            site = sites_collection[i]
            site_prop = site.Properties
            if site_prop["name"].Value == site_name:
                return site

        raise Exception("Site is not found: '{0}'".format(site_name))

    def map_path_get_paths(self, apps_collection, virt_path):
        """
        Helper to search app with virtual_path in apps collections.
        """
        result = ""
        found_virt_path = ""

        for ii in range(apps_collection.Count):
            app_prop = apps_collection[ii].Properties

            app_path = app_prop["path"].Value
            if virt_path.lower().startswith(app_path.lower()):
                vdir_collection = apps_collection[ii].Collection
                for iii in range(vdir_collection.Count):
                    vdir_prop = vdir_collection[iii].Properties
                    temp = combine_virtual_path(
                        app_path,
                        vdir_prop["path"].Value)
                    if virt_path.lower() == temp.lower():
                        result = vdir_prop["physicalPath"].Value
                        result = self.core.expandvars(result)
                        # exactly matched virtual dir
                        return result, virt_path

                    if virt_path.lower().startswith(temp.lower()):
                        result = vdir_prop["physicalPath"].Value
                        result = self.core.expandvars(result)
                        found_virt_path = temp
                # do not search in the other apps
                return result, found_virt_path

        # not found app
        return result, found_virt_path

    def map_path(self, site_name, virt_path):
        # найти физический путь по виртуальному
        # site_name='test wordpress 6301'   virt_path='/virt/virt2/wp-admin/config'
        # получить список виртуальных дирктория для сайта,
        # среди них найти самую вложенную подходящую для запроса /virt/virt2/
        # для нее найти путь
        # дописать остаток

        # много вложенных циклов не просто так, это ради оптимизации. так в 3-4 раза быстрее получилось
        # /app1/vit2/path/path/dir/
        # /app1/vit2/path234/path/dir/

        ah_write = self.get_iis_object()
        section = ah_write.GetAdminSection("system.applicationHost/sites", "MACHINE/WEBROOT/APPHOST")

        site = self.map_path_get_site(section.Collection, site_name)

        (result, found_virt_path) = self.map_path_get_paths(site.Collection, virt_path)

        if found_virt_path != "":
            # исправить хвост
            # /app1/vit2/path/path/dir/
            tail = virt_path[len(found_virt_path):]
            tail = tail.replace("/", os.path.sep)
            result = os.path.join(result, tail)
            return result

        return result

    def get_all_virtual_dirs(self, site_name):
        """
        Returns list of virtual directories for site
        """
        result = []

        site = self.get_site(site_name)
        for app in site.applications:
            app_path = app.path
            vdirs = self.get_app_virtual_directories(site_name, app_path)
            if app_path == "/":
                app_path = ""

            for virtual_directory in vdirs:
                result.append(virtual_directory)

        return result

    def get_subdirectories(self, physical_path):
        """
        Returns list of directories for physical path
        """
        result = []
        for p in os.listdir(physical_path):
            if not os.path.isdir(os.path.join(physical_path, p)):
                continue
            result.append(os.path.join(physical_path, p))

        return result

    def get_subvirtualdirectories(self, site_name, virt_path):
        """
        получить подпапки для виртуального пути, только на 1 уровень вглубь
        """
        result = []
        vdirs = self.get_all_virtual_dirs(site_name)
        for vdir in vdirs:
            if not vdir.path.lower().startswith(virt_path.lower()):
                continue  # skip
            if len(vdir.path.split("/")) - len(virt_path.split("/")) != 1:
                continue  # deep
            result.append(vdir)

        return result

    def remove_by_name(self, values, name):
        """
        Helper to remove list item with specified name attribute
        """
        for d in values:
            if d["name"] == name:
                values.remove(d)
                return



