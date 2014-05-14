# -*- python -*-
#
#       OpenAlea.OALab: Multi-Paradigm GUI
#
#       Copyright 2014 INRIA - CIRAD - INRA
#
#       File author(s): Julien Coste <julien.coste@inria.fr>
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################
"""
The Project is a structure which permit to manage different objects.

It store **metadata** (name, author, description, version, license, ...) and **data** (src, models, images, ...).

You have here the default architecture of the project named "name",
stored in your computer.

/name
    oaproject.cfg        (Configuration file)
    /src          (Files sources, Script Python, LPy...)
    /control       (Control, like color map or curve)
    /world          (scene, scene 3D)
    /cache          (Intermediary saved objects)
    /data           (Data files like images, .dat, ...)
    /startup          (Preprocessing scripts)
        *.py            (Preprocessing scripts)
        *import*.py     (Libs and packages to import in preprocessing)

:use:
    .. code-block:: python

        project1 = Project(name="mynewproj", path="/path/to/proj")
        project1.start()
        project1.add(category="src", name="hello.py", value="print 'Hello World'")
        project1.author = "John Doe"
        project1.description = "This project is used to said hello to everyone"
        project1.save()
"""

import os
import warnings
from openalea.core.path import path as path_
from openalea.vpltk.project.configobj import ConfigObj
from openalea.vpltk.project.loader import get_loader
from openalea.vpltk.project.saver import get_saver

def _model_factories():
    models = {}
    from openalea.vpltk.plugin import discover, Plugin
    plugins = discover('oalab.model')
    for plugin in plugins.values():
        model = Plugin(plugin)
        model = model.load()
        models[model.extension] = model
    return models

class Project(object):

    model_klasses = _model_factories()

    def __init__(self, name, path,
                 icon="", author="OpenAlea Consortium", author_email="",
                 description="", long_description="", citation="", url="", dependencies=[], license="CeCILL-C",
                 version="0.1"):
        """
        :param name: name of the project to create or load
        :param path: path of the project to create or load
        """
        # Metadata
        self.path = path_(path)
        self.metadata = {
            "name": str(name),
            "icon": path_(icon),
            "author": str(author),
            "author_email": str(author_email),
            "description": str(description),
            "long_description": str(long_description),
            "citation": str(citation),
            "url": str(url),
            "dependencies": dependencies,
            "license": str(license),
            "version": str(version),
        }
        self.config_file = "oaproject.cfg"

        # Data
        self.files = {
            "src": dict(),
            "control": dict(),
            "cache": dict(),
            "data": dict(),
            "world": dict(),
            "startup": dict(),
            "doc": dict()
        }

    #----------------------------------------
    # Public API
    #----------------------------------------
    def create(self):
        """
        Do the same thing that import method.

        .. seealso:: :func:`start` :func:`load` :func:`load_manifest`
        """
        warnings.warn("project.create() is deprecated. Please use project.start()")
        self.start()

    def start(self, shell=None, namespace={}):
        """
        1. :func:`load` objects into project.
        2. Import startup.
        3. Run preprocessing.

        :param shell: shell to run startup. Has to have the method "runcode(code)". Default, None.
        :param namespace: dict used to run the sources. Default, empty dict.

        .. seealso:: :func:`load` :func:`load_manifest`
        """
        # Load in object
        self.load()
        # Load in shell
        self._startup_import(shell, namespace)
        self._startup_run(shell, namespace)

    def load(self):
        """
        Realize a total loading of project (contrary to :func:`load_manifest`).

        1. Load manifest :func:`load_manifest`
        2. Read data files listed in manifest and fill project object.

        .. seealso:: :func:`start` :func:`load_manifest`
        """
        self.load_manifest()
        for category in self.files.keys():
            obj = self._load(str(category))
            setattr(self, category, obj)

    def save(self):
        """
        Save project on disk.

        1. Save **data** files.
        2. Save **metadata** and **list on previously saved data** into a manifest file (*oaproject.cfg*).

        .. seealso:: :func:`save_manifest`
        """
        for category in self.files.keys():
            self._save(str(category))
        self.save_manifest()

    def get(self, category, name):
        """
        Search an object inside project and return it.

        :param category: category of object to get
        :param name: name of object to get
        :return: object named *name* in the category *category* if it exists. Else, None.

        :use: >>> get(category="src", name="myscript.py")

        .. seealso:: :func:`add`
        """
        if hasattr(self, category):
            cat = getattr(self, category)
            if name in cat:
                return cat[name]
        return None

    def add(self, category, name, value):
        """
        Add an object in the project

        :param category: *type* of object to add ("src", "control", "world", ...)
        :param name: filename of the object to add (path or str)
        :param value: to add (string)

        .. seealso:: :func:`get` :func:`remove`
        """
        if not hasattr(self, category):
            setattr(self, category, dict())
        cat = getattr(self, category)
        cat[name] = value

    def remove(self, category, name):
        """
        Remove an object in the project

        Remove nothing on disk.

        :param category: category of object to remove ("src", "control", "world", ...) (str)
        :param name: filename of the src to remove (path or str)
        """
        category = str(category)
        filename = path_(name)

        if hasattr(self, category):
            cat = getattr(self, category)
            if filename in cat:
                del cat[filename]

    def rename(self, category, old_name, new_name):
        """
        Rename a src, a world or a control in the project.
        If category is project, rename the entire project.

        :param category: Can be "src", "control", "world" or "project" (str)
        :param old_name: current name of thing to rename (str)
        :param new_name: future name of thing to rename (str)
        """
        if (category == "project"):
            self.name = new_name
            self.save()
            if (self.path / old_name).exists():
                try:
                    (self.path / old_name).removedirs()
                except IOError:
                    pass
        else:
            if hasattr(self, category):
                cat = getattr(self, category)
                # Rename in project
                cat[str(new_name)] = cat[str(old_name)]
                # Remove inside project
                self.remove(category, old_name)
                # TODO: Remove on disk
                # temp_path = self.path / self.name / category / old_name
                # if temp_path.exists():
                #     try:
                #         path_(temp_path).removedirs()
                #     except IOError:
                #         pass

    #----------------------------------------
    # Manifest
    #----------------------------------------
    def save_manifest(self):
        """
        Save a manifest file on disk. His name is "*oaproject.cfg*".

        It contains **list of files** that are inside project (*manifest*) and **metadata** (author, version, ...).

        .. seealso:: :func:`load_manifest`
        """
        config = ConfigObj()
        config.filename = self.path / self.name / self.config_file

        config['metadata'] = dict()
        config['manifest'] = dict()

        config['metadata'] = self.metadata

        for files in self.files.keys():
            filenames = getattr(self, files)
            if filenames.keys():
                config['manifest'][files] = filenames.keys()

        config.write()

    def load_manifest(self):
        """
        *Partially load* a project from a manifest file.

        1. Read manifest file (oaproject.cfg).
        2. Load metadata inside project from manifest.
        3. Load **filenames** of data files inside project from manifest.
        4. **Not** load data ! If you want to load data, please use :func:`load`.

        :warning: load metadata and list of filenames but does not load files

        .. seealso:: :func:`save_manifest` :func:`load`
        """
        config = ConfigObj(self.path / self.name / self.config_file)
        if 'metadata' in config:
            for info in config["metadata"].keys():
                setattr(self, info, config['metadata'][info])

        if 'manifest' in config:
            # Load file names in good place (dict.keys()) but don't load entire object:
            # ie. load keys but not values
            for files in config["manifest"].keys():
                filedict = dict()
                for f in config['manifest'][files]:
                    filedict[f] = ""
                setattr(self, files, filedict)

    #----------------------------------------
    # model
    #----------------------------------------
    def model(self, name):
        """
        :param name: name of the file in self.src to convert into model. Can pass various names split by spaces. Can pass "*".
        :return: model object corresponding to the source named *name* in self.src. If various values, return a list of models. If failed, return None.
        """
        names = name.split()
        return_models = []

        if "*" in names and len(names) == 1:
            names = self.src.keys()

        for name in names:

            if name in self.src:
                # get code, filename and extension
                code = self.src[name]

                filename = path_(name)
                ext = filename.ext[1:]
                if ext in self.model_klasses:
                    return_models.append(self.model_klasses[ext](name=name, code=code))

        if len(return_models) == 1:
            return return_models[0]
        return return_models

    #----------------------------------------
    # src
    #----------------------------------------
    def add_script(self, name, script):
        """
        Add a src in the project

        :deprecated: replace by :func:`add` method
        :param name: filename of the src to add (path or str)
        :param script: to add (string)

        .. seealso:: :func:`add`
        """
        warnings.warn(
            "project.add_script(name, script) is deprecated. Please use project.add('src', name, script) instead.")
        self.add("src", name, script)

    def remove_script(self, name):
        """
        Add a src in the project

        Remove nothing on disk.

        :deprecated: replace by :func:`remove` method
        :param name: filename of the src to remove (path or str)

        .. seealso:: :func:`remove`
        """
        warnings.warn("project.remove_script(name) is deprecated. Please use project.remove('src', name) instead.")
        self.remove("src", name)

    def run_src(self, name, namespace={}):
        """
        Try to run the source file named *name* into current shell

        :param name: name of the source to run
        :param namespace: dict used to run the sources. Default, empty dict.
        """
        src = self.get("src", name)
        exec(src, namespace)

    #----------------------------------------
    # Protected
    #----------------------------------------
    def _load(self, object_type, namespace={}):
        """
        Load files listed in self.object_type.keys()

        :param namespace: dict used to run the sources. Default, empty dict.
        """
        object_type = str(object_type)
        return_object = dict()

        if hasattr(self, object_type):
            temp_path = self.path / self.name / object_type

            if not temp_path.exists():
                return return_object

            files = getattr(self, object_type)
            files = files.keys()
            for filename in files:
                filename = path_(filename)
                pathname = self.path / self.name / object_type / filename
                if filename.isabs():
                    # Load files that are outside project
                    pathname = filename
                Loader = get_loader("GenericLoader")
                if object_type == "control":
                    Loader = get_loader("CPickleLoader")
                if object_type == "world":
                    Loader = get_loader("BGEOMLoader")
                loader = Loader()
                result = loader.load(pathname)
                return_object[filename] = result

        # hack to add cache in namespace
        if object_type == "cache":
            for cache_name in return_object:
                namespace[cache_name] = eval(str(return_object[cache_name]), namespace)

        return return_object

    def _save(self, object_type):
        object_type = str(object_type)
        object_ = getattr(self, object_type)
        if object_:
            temp_path = self.path / self.name / object_type

            # Make default directories if necessary
            if not (self.path / self.name).exists():
                os.mkdir(self.path / self.name)
            if not temp_path.exists():
                os.mkdir(temp_path)

            for sub_object in object_:
                filename = temp_path / sub_object
                sub_object = path_(sub_object)
                Saver = get_saver()
                if sub_object.isabs():
                    # Permit to save object outside project
                    filename = sub_object
                if object_type == "world":
                    # Save PlantGL objects
                    Saver = get_saver("BGEOMSaver")
                elif object_type == "control":
                    Saver = get_saver("CPickleSaver")
                saver = Saver()
                saver.save(object_[sub_object], filename)

    def _save_scripts(self):
        warnings.warn("project._save_scripts is deprecated. Please use project._save('src') instead.")
        self._save("src")

    def _startup_import(self, shell=None, namespace={}):
        """
        :param shell: shell to run startup. Has to have the method "runcode(code)". Default, None.
        :param namespace: dict used to run the sources. Default, empty dict.
        """
        if not shell:
            shell = self.use_ipython()

        for s in self.startup:
            if s.find('import') != -1:
                exec (self.startup[s], namespace)
                if shell:
                    shell.runcode(self.startup[s])

    def _startup_run(self, shell=None, namespace={}):
        """
        :param shell: shell to run startup. Has to have the method "runcode(code)". Default, None.
        :param namespace: dict used to run the sources. Default, empty dict.
        """
        if not shell:
            shell = self.use_ipython()

        for s in self.startup:
            if s.find('import') == -1:
                exec (self.startup[s], namespace)
                if shell:
                    shell.runcode(self.startup[s])

    def __repr__(self):
        txt = "Project named " + str(self.name) + " in path " + str(self.path) + """.

"""
        for metada in self.metadata:
            if self.metadata[metada]:
                txt = txt + metada + " : " + str(self.metadata[metada]) + ". "

        txt = txt + """

"""
        for file_ in self.files:
            if self.files[file_]:
                txt = txt + file_ + " : " + str(self.files[file_])

        return txt

    def use_ipython(self):
        """
        :return: the ipython shell if it exists. Else, return None.
        """
        shell = None
        try:
            # Try to get automatically current IPython shell
            shell = get_ipython()
        except NameError:
            pass

        return shell

    def get_scene(self):
        """
        :return: self.world (dict)
        """
        return self.get_world()

    def get_world(self):
        """
        :return: self.world (dict)
        """
        return self.world

    def is_project(self):
        """
        :return: True
        """
        return True

    def is_script(self):
        """
        :return: False
        """
        return False

    # Metadata

    @property
    def name(self):
        return self.metadata["name"]

    @name.setter
    def name(self, value):
        self.metadata["name"] = value

    @property
    def icon(self):
        return self.metadata["icon"]

    @icon.setter
    def icon(self, value):
        self.metadata["icon"] = value

    @property
    def author(self):
        return self.metadata["author"]

    @author.setter
    def author(self, value):
        self.metadata["author"] = value

    @property
    def author_email(self):
        return self.metadata["author_email"]

    @author_email.setter
    def author_email(self, value):
        self.metadata["author_email"] = value

    @property
    def description(self):
        return self.metadata["description"]

    @description.setter
    def description(self, value):
        self.metadata["description"] = value

    @property
    def long_description(self):
        return self.metadata["long_description"]

    @long_description.setter
    def long_description(self, value):
        self.metadata["long_description"] = value

    @property
    def citation(self):
        return self.metadata["citation"]

    @citation.setter
    def citation(self, value):
        self.metadata["citation"] = value

    @property
    def url(self):
        return self.metadata["url"]

    @url.setter
    def url(self, value):
        self.metadata["url"] = value

    @property
    def dependencies(self):
        return self.metadata["dependencies"]

    @dependencies.setter
    def dependencies(self, value):
        self.metadata["dependencies"] = value

    @property
    def license(self):
        return self.metadata["license"]

    @license.setter
    def license(self, value):
        self.metadata["license"] = value

    @property
    def version(self):
        return self.metadata["version"]

    @version.setter
    def version(self, value):
        self.metadata["version"] = value

    @property
    def src(self):
        return self.files["src"]

    @src.setter
    def src(self, value):
        self.files["src"] = value

    @property
    def control(self):
        return self.files["control"]

    @control.setter
    def control(self, value):
        self.files["control"] = value

    @property
    def cache(self):
        return self.files["cache"]

    @cache.setter
    def cache(self, value):
        self.files["cache"] = value

    @property
    def data(self):
        return self.files["data"]

    @data.setter
    def data(self, value):
        self.files["data"] = value

    @property
    def scene(self):
        return self.files["world"]

    @scene.setter
    def scene(self, value):
        self.files["world"] = value

    @property
    def world(self):
        return self.files["world"]

    @world.setter
    def world(self, value):
        self.files["world"] = value

    @property
    def startup(self):
        return self.files["startup"]

    @startup.setter
    def startup(self, value):
        self.files["startup"] = value

    @property
    def doc(self):
        return self.files["doc"]

    @doc.setter
    def doc(self, value):
        self.files["doc"] = value

    @property
    def icon_path(self):
        icon_name = None
        if self.icon:
            if not self.icon.startswith(':'):
                # local icon
                icon_name = path_(self.path) / self.name / self.icon
        return icon_name
