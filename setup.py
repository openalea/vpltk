# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from openalea.deploy.metainfo import read_metainfo

_version = {}
with open("src/openalea/vpltk/version.py") as fp:
    exec(fp.read(), _version)
    version = _version["__version__"]


# Packages list, namespace and root directory of packages

packages=find_packages('src')
package_dir={'': 'src'}

# Define global variables
name = 'openalea.vpltk'
description = "PyQt compatibility package for OpenAlea."
long_description= "The OpenAlea.Vpltk package implements a dispatch layer to manage the compatibility with PyQt4, PyQt5 and PySide."
authors= "Christophe Pradal et al."
authors_email = "christophe.pradal@cirad.fr"
url = "https://github.com/openalea/vpltk"
license = "CeCILL"
# dependencies to other eggs
setup_requires = ['openalea.deploy']

setup(
    name=name,
    version=version,
    description=description,
    long_description=long_description,
    author=authors,
    author_email=authors_email,
    url=url,
    license=license,
    keywords='openalea',

    # package installation
    packages=packages,
    package_dir=package_dir,

    # Namespace packages creation by deploy
    #namespace_packages = [namespace],
    #create_namespaces = False,
    zip_safe=False,

    # Dependencies
    setup_requires=setup_requires,

    # Eventually include data in your package
    # (flowing is to include all versioned files other than .py)
    include_package_data=True,
    # (you can provide an exclusion dictionary named exclude_package_data to remove parasites).
    # alternatively to global inclusion, list the file to include
    package_data={'openalea.vpltk.qt': ['*.ui'], },

    # Declare scripts and wralea as entry_points (extensions) of your package
    entry_points={
        'plugin': ['vpltksample = openalea.vpltk.sample'],
    },
)
