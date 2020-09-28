"""base module for Importing python files and manipulating the data structures before integrating into  Object"""

import pkgutil
import os
from datetime import datetime
from importlib.machinery import SourceFileLoader
from myfunctions.listmods import to_list
import importlib
from importlib.abc import Loader
import glob


class ImportRepository:
    """Main class that contains importing relating functions and methods"""

    def __init__(self):
        self.generic_dictionary = {}

    def load_execute_modules(
            self,
            executed_function,
            input_package,
            *kwargs,
            given_module=None):
        """Load the Variables from a package and all contained submodules and classes,
        Define a specific package or A module (file) from the package
        """
        input_package = to_list(input_package)

        for package in input_package:
            detected_modules = self.detect_submodules(package)
            if given_module is None:
                for module_name in detected_modules:
                    full_module_name = package + '.' + module_name
                    self.generic_dictionary.update(
                        self._execute_function(
                            executed_function,
                            full_module_name,
                            module_name,
                            *kwargs))
            else:
                full_module_name = input_package[0] + '.' + given_module
                self.generic_dictionary.update(
                    self._execute_function(
                        executed_function,
                        full_module_name,
                        given_module,
                        *kwargs))
            return self.generic_dictionary

    @staticmethod
    def _execute_function(functionname, *args):
        return functionname(*args)

    @staticmethod
    def rpo(object_name):
        """Ignores an object that is an internal or private variable and any functions"""
        if not object_name.startswith('__') and not object_name.startswith(
                '_') and not callable(object_name):
            return object_name
        return None

    @staticmethod
    def path_finder(object_path, start_path=None, walk=True):
        """Smart path finder that searches from a start path to find nearest match and continues to search up to the root directory"""
        start_time = datetime.now()
        user_base, user_ext = os.path.splitext(object_path)
        unicode_path_base = user_base.replace('/', '\\')
        full_name = None
        if os.path.exists(object_path) is True:
            return os.path.abspath(object_path)
        if start_path:
            dir_path = start_path
        else:
            dir_path = os.path.dirname(os.path.realpath(__file__))
        split_paths = dir_path.split('\\')
        directory = split_paths[0]
        for i in range((len(split_paths)), 0, -1):
            crawler = split_paths[:i]
            joiner = '\\'.join(crawler)
            if walk is False:
                joiner = dir_path
            for root, dirs, files in os.walk(joiner):
                if user_ext is None or user_ext == '':
                    for name in dirs:
                        full_name = os.path.join(root, name)
                        if unicode_path_base == name:
                            if full_name:
                                return str(os.path.realpath(full_name))
                else:
                    for name in files:
                        (base, ext) = os.path.splitext(
                            name)  # split base and extension
                        if ext == user_ext:  # check the extension
                            if base in unicode_path_base:
                                full_name = os.path.join(root, name)
                                if unicode_path_base in full_name:
                                    if full_name:
                                        return str(os.path.realpath(full_name))
        timediff = (datetime.now() - start_time)
        time_s = (timediff.seconds + ((timediff.microseconds) / (1000000)))
        msg = (
            f'The system was searched recursively up to the {directory} drive, yet no file or folder path containing {object_path} was found. Check your provided file path and extension.\n (Processing time: {time_s} seconds) ')
        raise ValueError(msg)

    def filename(self, path):
        return os.path.basename(os.path.splitext(path)[0])

    def locate_package(self, packagename, walk=True, init=True):
        """This method verifies the existence of a package and returns the full path
        arguments:
        filename: The suspected name of the file being searched for
            ex: "path_manipulation.py"
        walk: walk is a boolean argument. A value of "True" will allow the file finder to search
              recursively on the current drive.
         """
        initstring = r'\__init__.py'
        if not isinstance(walk, bool):
            raise TypeError(
                'walk is a boolean argument, must be either True or False')
        if init is True:
            packagename = packagename + initstring
        return self.path_finder(packagename, walk=walk)

    def detect_submodules(self, package, init=True):
        """Import all submodules of a module, recursively, including subpackages"""
        package_path = self.locate_package(package, walk=True, init=init)
        found_package = SourceFileLoader(
            package, package_path).load_module(package)
        results = []
        for loader, name, is_pkg in pkgutil.walk_packages(
                found_package.__path__):
            results.append(name)
        return results

    def locate_python_subfiles(self, dir_path):
        dir_path = self.path_finder(dir_path)
        return [
            os.path.join(
                dir_path,
                f) for f in os.listdir(dir_path) if os.path.isfile(
                os.path.join(
                    dir_path,
                    f)) and os.path.splitext(f)[1] == '.py']

    def import_class(self, module_path, class_name=None):
        try:
            assert os.path.isfile(module_path) is True
        except AttributeError:
            raise ImportError(
                "Module file does not exist, ensure full path has been given")
        module_name = self.filename(module_path)
        if not class_name:
            class_name = module_name
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        try:
            klass = getattr(module, class_name)
            return klass, class_name
        except AttributeError as abe:
            raise ImportError(
                f"A module named {module_name}.py was found but it did not have a class named {class_name}") from abe

    def find_files(self, path, patterns):
        filelist = []
        for pattern in patterns:
            filelist = filelist + \
                glob.glob(f"{path}/**/{pattern}", recursive=True)
        return filelist
