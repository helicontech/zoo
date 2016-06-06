# -*- coding: utf-8 -*-

# A very simple setup script to create a single executable
#
# hello.py is a very simple 'Hello, world' type script which also displays the
# environment in which the script runs
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the script without Python

from cx_Freeze import setup, Executable
import sys
import os
from core import version
print("==========Building============")
SourcePath          = os.path.abspath(os.path.dirname(__file__))
WebZooFolder        = os.path.join("web", "zoo")

def zoopath(folder):
    return os.path.join(WebZooFolder, folder)

def fullpath(folder):
    return os.path.join(SourcePath, zoopath (folder))

def paths_tuple(folder):
    return (fullpath(folder), zoopath(folder))

executables = [
    Executable(os.path.join(SourcePath, "zoocmd.py"))
]

options = {
    'build_exe': {
        "packages":       ["os", "pymssql", "_mssql", "win32console"],
        "excludes":       ["tkinter"],
        'compressed':     False,
        "include_files":  [paths_tuple("jstemplates"),
                           paths_tuple("templates"),
                           paths_tuple("static")],
        'path':           sys.path + ['modules']
    }
}

#with open(os.path.join(SourcePath, "core", "version.py"), 'r') as file:
#    version = file.read()

setup(name        ='zoo',
      version     =version.VERSION,
      description ='Zoo executable',
      options     =options,
      executables =executables
      )
