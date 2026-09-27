import pytest
from evalx.cli import main


def test_cli_expr_flag(capsys):
    assert main(["-e", "10", "+", "20", "-", "(10 * 2)"]) == 0
    captured = capsys.readouterr()
    assert "10" in captured.out


def test_cli_positional_expr(capsys):
    assert main(["10 + 20 - (10 * 2)"]) == 0
    captured = capsys.readouterr()
    assert "10" in captured.out


def test_cli_raw_mode(capsys):
    assert main(["-r", "2 ^ 8"]) == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == "256"


def test_cli_card_mode(capsys):
    assert main(["-c", "10 + 5"]) == 0
    captured = capsys.readouterr()
    assert "EVALX CALCULATOR" in captured.out
    assert "15" in captured.out


def test_cli_with_variables(capsys):
    assert main(["x * 2 + y", "-v", "x=10", "-v", "y=5", "-r"]) == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == "25"


def test_cli_error_handling(capsys):
    assert main(["10 / 0"]) == 1
    captured = capsys.readouterr()
    assert "Division by zero" in captured.err
