# -*- coding: utf-8 -*-
#
# Copyright © 2011 Spyder
# Contributor: Pierre Raybaut
# Website: http://github.com/spyder-ide/spyder
#
# Copyright © 2012-2013 pyLot - andheo
# Contributor: Guillaume Baty
#
# Copyright © 2014 INRIA - CIRAD - INRA
# Contributor: Frédéric Boudon
# http://github.com/openalea/openalea
#
# Copyright © 2015 PyQode
# Contributor: Colin Duquesnoy
# Website: http://github.com/pyqode/pyqode.qt
#
# Copyright © 2018 INRIA - CIRAD
# Contributor: Christophe Pradal
# http://github.com/openalea/vpltk
#
# -------------------------------------------
# Licensed under the terms of the MIT License
# -------------------------------------------


import os
import sys
import logging

__version__ = '2.10.0'
is_pyqt46 = False

#: Qt API environment variable name
QT_API = 'QT_API'
#: names of the expected PyQt4 api
PYQT4_API = [
    'pyqt',  # name used in IPython.qt
    'pyqt4'  # pyqode.qt original name
]
#: names of the expected PyQt5 api
PYQT5_API = ['pyqt5']

#: names of the expected PySide api
PYSIDE_API = ['pyside']
PYSIDE2_API = ['pyside2']

QT_MODULE_NAME = None

# If IPython is installed, use its order to avoid multiple python-qt loads
try:
    from qtconsole.qt import api_opts
except ImportError:
    import openalea.vpltk.qt.qt_loaders
    QT_API_ORDER = ['pyqt5', 'pyside2', 'pyqt', 'pyside']
else:
    QT_API_ORDER = api_opts
_api_version = int(os.environ.setdefault('QT_API_VERSION', '2'))


def setup_apiv2():
    """
    Setup apiv2 when using PyQt4 and Python2.
    """
    # setup PyQt api to version 2
    if sys.version_info[0] == 2:
        logging.getLogger(__name__).debug(
            'setting up SIP API to version 2')
        import sip
        try:
            sip.setapi("QString", 2)
            sip.setapi("QVariant", 2)
        except ValueError:
            logging.getLogger(__name__).critical(
                "failed to set up sip api to version 2 for PyQt4")
            raise ImportError('PyQt4')


def load_pyside():
    global QT_MODULE_NAME
    logging.getLogger(__name__).debug('trying PySide')
    import PySide2
    os.environ[QT_API] = PYSIDE_API[0]
    logging.getLogger(__name__).debug('imported PySide')
    QT_MODULE_NAME = 'PySide2'


def load_pyqt5():
    global QT_MODULE_NAME, is_PyQt56, __version_info__
    logging.getLogger(__name__).debug('trying PyQt5')
    import PyQt5
    os.environ[QT_API] = PYQT5_API[0]
    setup_apiv2()
    logging.getLogger(__name__).debug('imported PyQt5')
    __version_info__ = tuple(__version__.split('.') + ['final', 1])
    is_PyQt56 = __version__.startswith('5.15')
    QT_MODULE_NAME = 'PyQt5'
    #print QT_MODULE_NAME+' used : '+PyQt_license_warning


def load_pyqt4():
    global QT_MODULE_NAME
    logging.getLogger(__name__).debug('trying PyQt4')
    import PyQt4
    os.environ[QT_API] = PYQT4_API[0]
    logging.getLogger(__name__).debug('imported PyQt4')
    QT_MODULE_NAME = 'PyQt4'
    #print QT_MODULE_NAME+' used : '+PyQt_license_warning


QT_API_LOADER = {}
for API in PYSIDE_API:
    QT_API_LOADER[API] = load_pyside
for API in PYQT5_API:
    QT_API_LOADER[API] = load_pyqt5
for API in PYQT4_API:
    QT_API_LOADER[API] = load_pyqt4


class PythonQtError(Exception):

    """
    Error raise if no bindings could be selected
    """
    pass


def autodetect():
    """
    Auto-detects and use the first available QT_API by importing them in order defined in QT_API_ORDER
    """
    logging.getLogger(__name__).debug('auto-detecting QT_API')
    for API in QT_API_ORDER:
        if API in QT_API_LOADER:
            try:
                QT_API_LOADER[API]()
            except ImportError:
                continue
            else:
                break


if QT_API in os.environ:
    # check if the selected QT_API is available
    try:
        if os.environ[QT_API].lower() in PYQT5_API:
            load_pyqt5()
        elif os.environ[QT_API].lower() in PYQT4_API:
            load_pyqt4()
        elif os.environ[QT_API].lower() in PYSIDE_API:
            load_pyside()
    except ImportError:
        logging.getLogger(__name__).warning(
            'failed to import the selected QT_API: %s',
            os.environ[QT_API])
        # use the auto-detected API if possible
        autodetect()
else:
    # user did not select a qt api, let's perform auto-detection
    autodetect()

import openalea.vpltk.qt.designer
