# -*- coding: utf-8 -*-


class AppPool(object):
    """
    Represents IIS application pool.
    """

    def __init__(self, name, dotnet_version, pipeline_type, bitness):
        self.name = name
        self.dotnet_version = dotnet_version
        self.pipeline_type = pipeline_type
        self.bitness = bitness

    def __str__(self):
        return "AppPool({0})".format(self.name)

    def to_dict(self):
        return dict(
            name=self.name,
            dotnet_version=self.dotnet_version,
            pipeline_type=self.pipeline_type,
            bitness=self.bitness
        )