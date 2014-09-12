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
from openalea.vpltk.model import PythonModel
from openalea.oalab.model.parse import parse_functions, parse_docstring, get_docstring

code = '''
"""
input = x=1, y=2
output = result
"""
result = x + y
'''


model, inputs_info, outputs_info = parse_docstring(code)
_init, _step, _animate, _run = parse_functions(code)
doc = get_docstring(code)

def test_run():
    model_src = '''"""input = x=1, y=2
output = result"""
result = x + y
'''
    model = PythonModel(code=model_src)
    assert model is not None
    assert model.outputs == []
    result = model()
    assert model.outputs == 3
    assert result == 3

    result = model.run(4)
    assert result == 6

    result = model.run(1, 1)
    assert result == 2

    result = model(5)
    assert result == 7

    result = model(3, 5)
    assert result == 8

    # model.inputs = 5, 6
    # result = model()
    # assert result == 11



def test_run_list():
    model_src = '''"""input = x, y=[1,2,3]
output = result"""
result = 0
for val in x:
    result += val
for val in y:
    result += val
'''
    model = PythonModel(code=model_src)
    assert model is not None
    assert model.outputs == []
    result = model([4])
    assert model.outputs == 10
    assert result == 10

    result = model.run([5])
    assert result == 11

    result = model.run([1, 1], [1, 1])
    assert result == 4

    result = model([2, 2], [2, 2])
    assert result == 8


def test_run_tuple():
    model_src = '''"""input = x, y=(1,2,3)
output = result"""
result = 0
for val in x:
    result += val
for val in y:
    result += val
'''
    model = PythonModel(code=model_src)
    assert model is not None
    assert model.outputs == []
    result = model([4])
    assert model.outputs == 10
    assert result == 10

    result = model.run([5])
    assert result == 11

    result = model.run([1, 1], [1, 1])
    assert result == 4

    result = model([2, 2], [2, 2])
    assert result == 8

    result = model.run((5,))
    assert result == 11

    result = model.run((1, 1), (1, 1))
    assert result == 4

    result = model((2, 2), [2, 2])
    assert result == 8


def test_recursif():
    model_src = '''"""input = x
output = result"""
result = x + 1
'''
    model = PythonModel(code=model_src)
    result = model(model(model(model(model(1)))))
    assert result == 6


def test_fibonacci():
    model_fibo_src = '''"""
Compute one step of Fibonacci sequence.

Take in inputs x(i) and x(i+1) and return x(i+1) and x(i+2).

input = a, b
output = b, r
"""

r = a + b
'''
    fibo = PythonModel(code=model_fibo_src)
    xi, xj = 0, 1
    nb_step = 20
    for i in range(int(nb_step) - 1):
        xi, xj = fibo(xi, xj)

    assert xi == 4181
    assert xj == 6765


def test_kwargs():
    model_src = '''"""input = x=1, y=2
output = result"""
result = x + y
'''
    model = PythonModel(code=model_src)
    result = model(0, 1)
    assert result == 1
    result = model(x=2, y=2)
    assert result == 4
    result = model(x=3)
    assert result == 5
    result = model(y=3)
    assert result == 4


def test_step():
    model_src = '''"""
output = a"""
a = 0
N = 10

def init():
    a = 0

def step():
    a = a + 1

def animate():
    for i in range(N):
        a = a + 1

'''
    model = PythonModel(code=model_src)

    result = model()
    assert result == 0

    result = model.step()
    assert result == 1
    result = model.step()
    assert result == 2
    result = model.step()
    assert result == 3

    result = model.init()
    assert result == 0

    result = model.animate()
    assert result == 10


def test_step_animate():
    model_src = '''"""
output = a"""
a = 0
N = 10

def init():
    global a
    a = 0

def step():
    global a
    a = a + 1

def animate():
    for i in range(N):
        # Call function define before
        step()

'''
    model = PythonModel(code=model_src)

    result = model()
    assert result == 0

    result = model.step()
    assert result == 1
    result = model.step()
    assert result == 2
    result = model.step()
    assert result == 3

    result = model.init()
    assert result == 0

    result = model.animate()
    assert result == 10


def test_step_without_run():
    model_src = '''"""
output = a"""
def init():
    global a
    a = 0

def step():
    global a
    a = a + 1
'''
    model = PythonModel(code=model_src)

    result = model.init()
    assert result == 0

    result = model.step()
    assert result == 1
    result = model.step()
    assert result == 2
    result = model.step()
    assert result == 3

    result = model.init()
    assert result == 0
