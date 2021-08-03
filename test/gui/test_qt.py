def test_import_qt():
	try:
		from openalea.vpltk.qt import QtCore, QtGui
		result = True
	except ImportError:
		result = False
	assert result is True
	
def test_has_pyqt():
	from openalea.vpltk.check.qt import has_pyqt4, has_pyqt5
	result = has_pyqt4() or has_pyqt5()
	assert result is True
	