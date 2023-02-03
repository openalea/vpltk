def test_import_qt():
	try:
		from qtpy import QtCore, QtGui
		result = True
	except ImportError:
		result = False
	assert result is True
	
def test_has_pyqt():
	# from openalea.vpltk.check.qt import has_pyqt4
	# result = has_pyqt4()
	# assert result is True
	try:
		import PyQt5
		result = True
	except ImportError:
		result = False
	assert result is True
	