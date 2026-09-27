import pytest
from evalx.evaluator import MathEvaluator, EvaluationError
import math


def test_basic_arithmetic():
    ev = MathEvaluator()
    assert ev.eval("10 + 20") == 30
    assert ev.eval("100 - 45") == 55
    assert ev.eval("6 * 7") == 42
    assert ev.eval("15 / 3") == 5.0
    assert ev.eval("17 // 3") == 5
    assert ev.eval("17 % 5") == 2


def test_user_requested_expression():
    ev = MathEvaluator()
    # 10 + 20 - (10 * 2) = 30 - 20 = 10
    assert ev.eval("10 + 20 - (10 * 2)") == 10


def test_operator_precedence_and_grouping():
    ev = MathEvaluator()
    assert ev.eval("2 + 3 * 4") == 14
    assert ev.eval("(2 + 3) * 4") == 20
    assert ev.eval("2 ^ 3") == 8
    assert ev.eval("2 ** 3") == 8
    assert ev.eval("-5 + 10") == 5
    assert ev.eval("-(5 + 10)") == -15


def test_floating_point():
    ev = MathEvaluator()
    assert pytest.approx(ev.eval("0.1 + 0.2"), 0.0001) == 0.3
    assert pytest.approx(ev.eval("10 / 4"), 0.0001) == 2.5


def test_math_functions():
    ev = MathEvaluator()
    assert ev.eval("sqrt(16)") == 4.0
    assert ev.eval("abs(-42)") == 42
    assert ev.eval("factorial(5)") == 120
    assert ev.eval("fact(4)") == 24
    assert ev.eval("ceil(4.2)") == 5
    assert ev.eval("floor(4.8)") == 4
    assert ev.eval("gcd(54, 24)") == 6
    assert pytest.approx(ev.eval("sin(pi / 2)"), 0.0001) == 1.0
    assert pytest.approx(ev.eval("cos(0)"), 0.0001) == 1.0


def test_math_constants():
    ev = MathEvaluator()
    assert ev.eval("pi") == math.pi
    assert ev.eval("e") == math.e
    assert pytest.approx(ev.eval("2 * pi * 5"), 0.0001) == 31.4159265


def test_variables():
    ev = MathEvaluator(variables={"x": 10, "y": 3})
    assert ev.eval("x + y") == 13
    assert ev.eval("x * y + 2") == 32
    ev.set_variable("z", 50)
    assert ev.eval("z / x") == 5.0


def test_safety_and_errors():
    ev = MathEvaluator()
    with pytest.raises(EvaluationError, match="Division by zero"):
        ev.eval("10 / 0")

    with pytest.raises(EvaluationError, match="Complex function calls are not permitted"):
        ev.eval("__import__('os').system('ls')")

    with pytest.raises(EvaluationError):
        ev.eval("open('/etc/passwd')")

    with pytest.raises(EvaluationError, match="Empty expression"):
        ev.eval("   ")

    with pytest.raises(EvaluationError, match="Exponent too large"):
        ev.eval("2 ^ 100000")
