# -*- coding: utf-8 -*-
# -*- python -*-
#
#       Copyright © 2011 Pierre Raybaut
#       Copyright © 2012-2013 pyLot - andheo
#       Copyright © 2015 INRIA - CIRAD - INRA
#
#       File author(s): Pierre Raybaut
#
#       File contributor(s): Guillaume Baty
#
#       Licensed under the terms of the MIT License
#       (see spyderlib/__init__.py for details)
#       Spyderlib WebSite : https://github.com/spyder-ide/spyder
#
###############################################################################

"""
spyderlib.qt.compat
-------------------

Transitional module providing compatibility functions intended to help 
migrating from PyQt to PySide.

This module should be fully compatible with:
    * PyQt >=v4.4
    * both PyQt API #1 and API #2
    * PySide
"""

import os
import sys
from openalea.vpltk.qt.QtGui import QFileDialog

try:
    from openalea.core.path import path as Path
except ImportError:
    FilePath = DirPath = Path = str
else:
    FilePath = DirPath = Path


def arrange_path(path, path_class=Path):
    u"""
    Return a Path, FilePath or DirPath dependings on path nature.
    Path is used for special path like device "files" or path not existing on disk.
    If path is empty, returns None.

    If path do not exists on disk or is not file nor directory
    (like /dev/xyz on linux),it return a path_class.
    """
    if not path:
        return None
    path = Path(unicode(path))
    if path.isfile():
        return FilePath(path)
    elif path.isdir():
        return DirPath(path)
    else:
        return path_class(path)

#===============================================================================
# QVariant conversion utilities
#===============================================================================

PYQT_API_1 = False
if os.environ['QT_API'] == 'pyqt':
    import sip
    try:
        PYQT_API_1 = sip.getapi('QVariant') == 1 # PyQt API #1
    except AttributeError:
        # PyQt <v4.6
        PYQT_API_1 = True

    def to_qvariant(pyobj=None):
        """Convert Python object to QVariant
        This is a transitional function from PyQt API #1 (QVariant exist) 
        to PyQt API #2 and Pyside (QVariant does not exist)"""
        if PYQT_API_1:
            # PyQt API #1
            from PyQt4.QtCore import QVariant
            return QVariant(pyobj)
        else:
            # PyQt API #2
            return pyobj

    def from_qvariant(qobj=None, convfunc=None):
        """Convert QVariant object to Python object
        This is a transitional function from PyQt API #1 (QVariant exist) 
        to PyQt API #2 and Pyside (QVariant does not exist)"""
        if PYQT_API_1:
            # PyQt API #1
            assert callable(convfunc)
            if convfunc in (unicode, str):
                return convfunc(qobj.toString())
            elif convfunc is bool:
                return qobj.toBool()
            elif convfunc is int:
                return qobj.toInt()[0]
            elif convfunc is float:
                return qobj.toDouble()[0]
            else:
                return convfunc(qobj)
        else:
            # PyQt API #2
            return qobj
else:
    def to_qvariant(obj=None):  # analysis:ignore
        """Convert Python object to QVariant
        This is a transitional function from PyQt API#1 (QVariant exist) 
        to PyQt API#2 and Pyside (QVariant does not exist)"""
        return obj

    def from_qvariant(qobj=None, pytype=None):  # analysis:ignore
        """Convert QVariant object to Python object
        This is a transitional function from PyQt API #1 (QVariant exist) 
        to PyQt API #2 and Pyside (QVariant does not exist)"""
        return qobj


def getexistingdirectory(parent=None, caption='', basedir='',
                         options=QFileDialog.ShowDirsOnly):
    """Wrapper around QtGui.QFileDialog.getExistingDirectory static method
    Compatible with PyQt >=v4.4 (API #1 and #2) and PySide >=v1.0"""
    # Calling QFileDialog static method
    if sys.platform == "win32":
        # On Windows platforms: redirect standard outputs
        _temp1, _temp2 = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = None, None
    try:
        result = QFileDialog.getExistingDirectory(parent, caption, basedir,
                                                  options)
    finally:
        if sys.platform == "win32":
            # On Windows platforms: restore standard outputs
            sys.stdout, sys.stderr = _temp1, _temp2
    if not isinstance(result, basestring):
        # PyQt API #1
        result = arrange_path(result, path_class=Path)
    return result


def _qfiledialog_wrapper(attr, parent=None, caption=u'', basedir=u'',
                         filters=u'', selectedfilter=u'', options=None,
                         path_class=Path):
    if options is None:
        options = QFileDialog.Options(0)
    try:
        # PyQt <v4.6 (API #1)
        from Qt4.QtCore import QString
    except ImportError:
        # PySide or PyQt >=v4.6
        QString = None
    tuple_returned = True
    try:
        # PyQt >=v4.6
        func = getattr(QFileDialog, attr + 'AndFilter')
    except AttributeError:
        # PySide or PyQt <v4.6
        func = getattr(QFileDialog, attr)
        if QString is not None:
            selectedfilter = QString()
            tuple_returned = False

    # Calling QFileDialog static method
    if sys.platform == "win32":
        # On Windows platforms: redirect standard outputs
        _temp1, _temp2 = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = None, None
    try:
        result = func(parent, caption, basedir,
                      filters)
    finally:
        if sys.platform == "win32":
            # On Windows platforms: restore standard outputs
            sys.stdout, sys.stderr = _temp1, _temp2

    # Processing output
    if tuple_returned:
        # PySide or PyQt >=v4.6
        output, selectedfilter = result
    else:
        # PyQt <v4.6 (API #1)
        output = arrange_path(result, path_class=path_class)

    if QString is not None:
        # PyQt API #1: conversions needed from QString/QStringList
        selectedfilter = unicode(selectedfilter)
        if isinstance(output, QString):
            # Single filename
            output = unicode(output)
        elif output is None:
            pass
        else:
            # List of filenames
            output = [unicode(fname) for fname in output]

    if isinstance(output, unicode):
        # Single filename
        output = arrange_path(output, path_class=path_class)
    elif isinstance(output, list):
        output = [arrange_path(fname, path_class=path_class) for fname in output]
    else:
        output = None

    # Always returns the tuple (output, selectedfilter)
    return output, selectedfilter


def getopenfilename(parent=None, caption=u'', basedir=u'', filters=u'',
                    selectedfilter=u'', options=None):
    """Wrapper around QtGui.QFileDialog.getOpenFileName static method
    Returns a tuple (filename, selectedfilter) -- when dialog box is canceled,
    returns a tuple of empty strings
    Compatible with PyQt >=v4.4 (API #1 and #2) and PySide >=v1.0"""
    return _qfiledialog_wrapper('getOpenFileName', parent=parent,
                                caption=caption, basedir=basedir,
                                filters=filters, selectedfilter=selectedfilter,
                                options=options, path_class=FilePath)


def getopenfilenames(parent=None, caption=u'', basedir=u'', filters=u'',
                     selectedfilter=u'', options=None):
    """Wrapper around QtGui.QFileDialog.getOpenFileNames static method
    Returns a tuple (filenames, selectedfilter) -- when dialog box is canceled,
    returns a tuple (empty list, empty string)
    Compatible with PyQt >=v4.4 (API #1 and #2) and PySide >=v1.0"""
    return _qfiledialog_wrapper('getOpenFileNames', parent=parent,
                                caption=caption, basedir=basedir,
                                filters=filters, selectedfilter=selectedfilter,
                                options=options, path_class=FilePath)


def getsavefilename(parent=None, caption=u'', basedir=u'', filters=u'',
                    selectedfilter=u'', options=None):
    """Wrapper around QtGui.QFileDialog.getSaveFileName static method
    Returns a tuple (filename, selectedfilter) -- when dialog box is canceled,
    returns a tuple of empty strings
    Compatible with PyQt >=v4.4 (API #1 and #2) and PySide >=v1.0"""
    return _qfiledialog_wrapper('getSaveFileName', parent=parent,
                                caption=caption, basedir=basedir,
                                filters=filters, selectedfilter=selectedfilter,
                                options=options, path_class=FilePath)
