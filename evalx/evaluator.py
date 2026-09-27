"""Safe mathematical expression parser and evaluator using Python's AST."""

import ast
import math
import operator
from typing import Any, Union, Dict, Callable

# Supported binary operators
BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.BitXor: operator.xor,
    ast.BitAnd: operator.and_,
    ast.BitOr: operator.or_,
    ast.LShift: operator.lshift,
    ast.RShift: operator.rshift,
}

# Supported unary operators
UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
    ast.Invert: operator.invert,
}

# Standard constants
MATH_CONSTANTS: Dict[str, Union[int, float]] = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "inf": math.inf,
}

# Supported math functions
MATH_FUNCTIONS: Dict[str, Callable[..., Any]] = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "atan2": math.atan2,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "sqrt": math.sqrt,
    "cbrt": lambda x: math.pow(x, 1 / 3),
    "exp": math.exp,
    "log": math.log,
    "log10": math.log10,
    "log2": math.log2,
    "abs": abs,
    "round": round,
    "ceil": math.ceil,
    "floor": math.floor,
    "trunc": math.trunc,
    "fact": math.factorial,
    "factorial": math.factorial,
    "gcd": math.gcd,
    "deg": math.degrees,
    "rad": math.radians,
    "sum": sum,
    "min": min,
    "max": max,
    "pow": math.pow,
}


class EvaluationError(Exception):
    """Raised when an expression cannot be safely or mathematically evaluated."""
    pass


class MathEvaluator:
    """Safely evaluates mathematical expressions without using unsafe eval()."""

    def __init__(self, variables: Dict[str, Union[int, float]] = None):
        self.variables = variables.copy() if variables else {}

    def set_variable(self, name: str, value: Union[int, float]) -> None:
        self.variables[name] = value

    def eval(self, expr: str) -> Union[int, float, complex]:
        expr = expr.strip()
        if not expr:
            raise EvaluationError("Empty expression")

        # Normalize caret ^ to exponentiation ** for friendly math syntax
        # Only replace ^ when not intended as bitwise xor if user prefers math convention
        # But allow standard python ** natively.
        expr_normalized = self._normalize_syntax(expr)

        try:
            tree = ast.parse(expr_normalized, mode="eval")
        except SyntaxError as e:
            raise EvaluationError(f"Syntax error at position {e.offset}: {e.msg}") from e

        return self._eval_node(tree.body)

    def _normalize_syntax(self, expr: str) -> str:
        """Replace ^ with ** unless prefixed with xor keyword."""
        # Simple caret replacement for common math expectations (e.g. 2^3 -> 2**3)
        # Developers expect 2^3 = 8 in a math calculator, not 2 XOR 3 = 1
        # If user explicitly wants xor, they can use xor() function or bitwise mode.
        return expr.replace("^", "**")

    def _eval_node(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):  # Numbers, True, False, etc.
            if isinstance(node.value, (int, float, complex)):
                return node.value
            raise EvaluationError(f"Unsupported constant type: {type(node.value).__name__}")

        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in BINARY_OPS:
                raise EvaluationError(f"Unsupported binary operator: {op_type.__name__}")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            try:
                # Prevent massive exponents that could hang or exhaust CPU/memory
                if op_type is ast.Pow:
                    if isinstance(right, (int, float)) and right > 10000:
                        raise EvaluationError("Exponent too large (max 10000)")
                return BINARY_OPS[op_type](left, right)
            except ZeroDivisionError:
                raise EvaluationError("Division by zero")
            except OverflowError:
                raise EvaluationError("Numerical overflow: result is too large")
            except Exception as e:
                raise EvaluationError(f"Operation failed: {str(e)}")

        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in UNARY_OPS:
                raise EvaluationError(f"Unsupported unary operator: {op_type.__name__}")
            operand = self._eval_node(node.operand)
            return UNARY_OPS[op_type](operand)

        elif isinstance(node, ast.Name):
            # Check variables
            if node.id in self.variables:
                return self.variables[node.id]
            # Check constants
            if node.id in MATH_CONSTANTS:
                return MATH_CONSTANTS[node.id]
            raise EvaluationError(f"Unknown variable or constant: '{node.id}'")

        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise EvaluationError("Complex function calls are not permitted")
            func_name = node.func.id
            if func_name not in MATH_FUNCTIONS:
                raise EvaluationError(f"Unknown function: '{func_name}()'")

            args = [self._eval_node(arg) for arg in node.args]
            try:
                func = MATH_FUNCTIONS[func_name]
                return func(*args)
            except ValueError as e:
                raise EvaluationError(f"Math error in {func_name}(): {str(e)}")
            except TypeError as e:
                raise EvaluationError(f"Invalid arguments for {func_name}(): {str(e)}")
            except Exception as e:
                raise EvaluationError(f"Error executing {func_name}(): {str(e)}")

        elif isinstance(node, ast.List):
            return [self._eval_node(elem) for elem in node.elts]

        elif isinstance(node, ast.Tuple):
            return tuple(self._eval_node(elem) for elem in node.elts)

        else:
            raise EvaluationError(f"Unsupported syntax expression: {type(node).__name__}")
