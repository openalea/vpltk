

from openalea.vpltk.qt import QtGui
import random
from openalea.oalab.project.projectwidget import ProjectManagerWidget
from openalea.core.project.manager import ProjectManager
from openalea.oalab.session.session import Session
from openalea.core.path import tempdir


def new_tmp_project(projectdir):
    pm = ProjectManager()
    project = pm.create('tmpproject', projectdir=projectdir)
    pm.cproject = project
    return project


def add_lot_of_data(project, category='model', n=10):
    for i in range(n):
        project.add(category, filename='%s_%05d.ext' % (category, i))


def load_all_projects():
    projects = list(pm.search())
    random.shuffle(projects)
    for proj in projects:
        print 'load', proj
        pm.cproject = proj

if __name__ == '__main__':
    tmp = tempdir()

    instance = QtGui.QApplication.instance()
    if instance is None:
        app = QtGui.QApplication([])
    else:
        app = instance

    session = Session()
    pm = ProjectManager()
    pm.discover()
    pmw = ProjectManagerWidget()
    pmw.initialize()
#     pm.load('mtg')

    from openalea.oalab.shell import get_shell_class
    from openalea.core.service.ipython import interpreter as interpreter_

    # Set interpreter
    interpreter = interpreter_()
    interpreter.user_ns['interp'] = interpreter
    interpreter.user_ns.update(locals())
    interpreter.user_ns['pmw'] = pmw
    interpreter.user_ns['pm'] = pm
    # Set Shell Widget

    widget = QtGui.QWidget()
    layout = QtGui.QHBoxLayout(widget)

    shellwdgt = get_shell_class()(interpreter)

    layout.addWidget(pmw)
    layout.addWidget(shellwdgt)

    layout.setSpacing(0)
    layout.setContentsMargins(0, 0, 0, 0)

    widget.show()
    widget.raise_()

    if instance is None:
        app.exec_()

    tmp.rmtree()
