"""
Provides widget classes and functions.

.. warning:: All PyQt5/PySide gui classes are exposed but when you use
    PyQt5, those classes are not available. Therefore, you should treat/use
    this package as if it was ``PyQt5.QtWidgets`` module.
"""
import os
from openalea.vpltk.qt import QT_API
from openalea.vpltk.qt import PYQT5_API
from openalea.vpltk.qt import PyQt5_API
from openalea.vpltk.qt import PYSIDE_API
from PyQt5.QtWidgets import *

if os.environ[QT_API] in PYQT5_API:
    from PyQt5.QtWidgets import *
elif os.environ[QT_API] in PyQt5_API:
    from PyQt5.QtWidgets import *
    from PyQt5.QtWidgets import QFileDialog as OldFileDialog

    class QFileDialog(OldFileDialog):

        @staticmethod
        def getOpenFileName(parent=None, caption='', directory='',
                            filter='', selectedFilter='',
                            options=OldFileDialog.Options()):
            return OldFileDialog.getOpenFileNameAndFilter(
                parent, caption, directory, filter, selectedFilter,
                options)

        @staticmethod
        def getOpenFileNames(parent=None, caption='', directory='',
                             filter='', selectedFilter='',
                             options=OldFileDialog.Options()):
            return OldFileDialog.getOpenFileNamesAndFilter(
                parent, caption, directory, filter, selectedFilter,
                options)

        @staticmethod
        def getSaveFileName(parent=None, caption='', directory='',
                            filter='', selectedFilter='',
                            options=OldFileDialog.Options()):
            return OldFileDialog.getSaveFileNameAndFilter(
                parent, caption, directory, filter, selectedFilter,
                options)
elif os.environ[QT_API] in PYSIDE_API:
    from PySide2.QtGui import *
