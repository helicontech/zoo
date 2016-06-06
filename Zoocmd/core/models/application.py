# -*- coding: utf-8 -*-



from core.models.engine import Engine
from core.models.base_product import BaseProduct
from core.exception import ProductNotFoundError
from core.parameters_manager import KnownParameters
from core.helpers.common import expand_env_variables



import logging
from collections import OrderedDict
import os

class Application(BaseProduct):
    """
    Represents Application (product type).
    See BaseProduct class for comments.
    Differences from BaseProduct:
    - additional attrs: engines, database_type, start_page
    - creating .zoo file after installation
    - manage engines
    """

    def __init__(self, core, attrs = None):
        super().__init__(core, attrs)
        self.iis = self.core.api.os.web_server
        # supported engines with configs
        if attrs is None:
            attrs = {}

        self.engines = attrs.get('engines', None)

        self.locations = attrs.get('locations', None)
        # list of supported database types
        self.database_type = attrs.get('database_type', None)
        # start page that we need show after installation
        self.start_page = attrs.get('start_page', None)
        self.selected_engine = None

    def get_typename(self):
        return 'application'

    def merge(self, **kwargs):
        super().merge(**kwargs)
        # merge additional fields
        self.engines = kwargs.get('engines') or self.engines
        self.database_type = kwargs.get('database_type') or self.database_type
        self.start_page = kwargs.get('start_page') or self.start_page
        self.locations = kwargs.get('locations') or self.locations

    def __getstate__(self):
        result = super().__getstate__()
        # additional fields
        result['engines'] = self.engines
        result['database_type'] = self.database_type
        result['start_page'] = self.start_page
        result["locations"] = self.locations
        return result

    def install(self, parameters):
        """
        Installs application.
        Creates .zoo file with zoo app config.
        """
        # setup engine variables
        # emulate zoo module variables

        APPL_PHYSICAL_PATH = parameters[KnownParameters.PHYSICAL_PATH.value]
        APPL_PHYSICAL_SHORT_PATH = self.core.api.os.shell.get_short_path_name(parameters[KnownParameters.PHYSICAL_PATH.value])
        APPL_VIRTUAL_PATH = parameters["app-name"]
        APPL_ID = parameters["app-name"].replace("/", "")
        os.environ["APPL_PHYSICAL_PATH"] = APPL_PHYSICAL_PATH
        os.environ["APPL_PHYSICAL_SHORT_PATH"] = APPL_PHYSICAL_SHORT_PATH
        os.environ["APPL_VIRTUAL_PATH"] = APPL_VIRTUAL_PATH
        os.environ["APPL_ID"] = APPL_ID


        application_config = self.create_config(parameters)
        std_env = os.environ.copy()
        zoo_env = self.core.api.os.web_server.create_environment(application_config, std_env)

        for env_var in zoo_env:
            if len(zoo_env[env_var]) > 0:
                os.environ[env_var] = zoo_env[env_var]
        # print(os.environ)
        result = super().install(parameters)
        if not result:
            return False

        self.create_zoo_file(APPL_PHYSICAL_PATH, application_config)
        return True

    def create_config(self, parameters):
        """
        Creates config dict that can be save as  .zoo config  file for installed zoo app.
        :param parameters:
        :return:
        """
        # get engine
        engine = self.get_selected_engine()
        # .zoo file data
        config = OrderedDict()
        # save application representation
        app = self.to_dict(rich=True)
        config['application'] = app
        # save install parameters
        if parameters is None:
            parameters = {}
        app['parameters'] = parameters
        # always must be
        parameters['selected-engine'] = engine.name
        # if maintainer forgot about application
        logging.debug("create zoo config from %s" % str(app))
        if 'locations' not in app or app['locations'] is None or not app['locations']:
            app['locations'] = [{"path": "*", "engine": engine.name}]
        return config

    def create_zoo_file(self, physical_path, config):

        # save .zoo file
        engine = config["application"]['parameters']['selected-engine']
        # change selected engine to existed value
        for i in config['application']['locations']:
            if i['engine'] == 'selected-engine':
                i['engine'] = engine

        self.iis.create_zoo_config(physical_path, config)

    def set_select_engine(self, engine):
        """
        Sets engine for zoo app, this engine will be saved in .zoo file.
        This method is called by installed_manager to set zoo app engine.
        Real engine selection appears in Core.install() on 'engine = dependency_manager.get_engine(products)'
        :type engine: core.models.engine.Engine
        """
        if engine is None:
            raise Exception("can't set engine, engine is null")
        logging.info('Engine {0} selected for {1}'.format(engine, self))
        self.selected_engine = engine

    def get_selected_engine(self):
        """
        Returns selected engine for zoo app.
        """
        if not isinstance(self.selected_engine, Engine):
            raise ProductNotFoundError("Can\'t find selected engine '{0}' for '{1}'".format(self.selected_engine,
                                                                                            self.name))
        return self.selected_engine

    def get_settings_for_engine(self, engine_object)-> OrderedDict:
        """
        Returns OrderedDict with settings for engine.
        This settings will be saved in .zoo file.
        """
        name = engine_object.name
        result = OrderedDict()
        if self.engines:
            for app_engine in self.engines:
                if app_engine['engine'].lower() == name.lower():
                    result = app_engine
                    return result

        logging.warning("Can't find engine '{0}'".format(name))
        return result

