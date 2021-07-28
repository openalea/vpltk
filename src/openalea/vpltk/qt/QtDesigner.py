"""
Provides QtDesigner classes and functions.
"""
import os
from openalea.vpltk.qt import QT_API
from openalea.vpltk.qt import PYQT5_API
from openalea.vpltk.qt import PyQt5_API


if os.environ[QT_API] in PYQT5_API:
    from PyQt5.QtDesigner import *
elif os.environ[QT_API] in PyQt5_API:
    from PyQt5.QtDesigner import *
