"""
Provides QtCore classes and functions.
"""
import os
from openalea.vpltk.qt import QT_API
from openalea.vpltk.qt import PYQT5_API
from openalea.vpltk.qt import PYQT4_API
from openalea.vpltk.qt import PYSIDE_API
from openalea.vpltk.qt import PYSIDE2_API

if os.environ[QT_API] in PYQT5_API:
    from PyQt5.QtCore import *
    # compatibility with pyside
    from PyQt5.QtCore import pyqtSignal as Signal
    from PyQt5.QtCore import pyqtSlot as Slot
    from PyQt5.QtCore import pyqtProperty as Property
    # use a common __version__
    from PyQt5.QtCore import QT_VERSION_STR as __version__
elif os.environ[QT_API] in PYQT4_API:
    from PyQt4.QtCore import *
    # compatibility with pyside
    from PyQt4.QtCore import pyqtSignal as Signal
    from PyQt4.QtCore import pyqtSlot as Slot
    from PyQt4.QtCore import pyqtProperty as Property
    from PyQt4.QtCore import QSortFilterProxyModel
    # use a common __version__
    from PyQt4.QtCore import QT_VERSION_STR as __version__
elif os.environ[QT_API] in PYSIDE_API:
    from PySide.QtCore import *
    from PySide.QtGui import QSortFilterProxyModel
    # use a common __version__
    import PySide.QtCore
    __version__ = PySide.QtCore.__version__
elif os.environ[QT_API] in PYSIDE2_API:
    from PySide2.QtCore import *
    import PySide2.QtCore
