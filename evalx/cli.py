"""Command line interface for evalx."""

import sys
import argparse
from typing import List, Optional

from evalx.evaluator import MathEvaluator, EvaluationError, MATH_FUNCTIONS, MATH_CONSTANTS
from evalx.formatter import render_card, format_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="evalx",
        description="A fast, safe, and beautiful terminal mathematical calculator.",
        epilog="Examples:\n"
               "  evalx '10 + 20 - (10 * 2)'\n"
               "  evalx -e 10 + 20 - '(10 * 2)'\n"
               "  evalx 'sin(pi / 4) + sqrt(16)'\n"
               "  evalx 'x^2 + y' -v x=5 -v y=10\n"
               "  evalx --raw '2^16'\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Flag-style expression
    parser.add_argument(
        "-e", "--expr",
        dest="expr_flag",
        nargs="*",
        help="Expression to evaluate (tokens are automatically joined)",
    )

    # Positional expression tokens (allows: evalx 10 + 20)
    parser.add_argument(
        "positional_expr",
        nargs="*",
        help="Expression tokens",
    )

    # Variable bindings (-v x=10 -v y=20)
    parser.add_argument(
        "-v", "--var",
        dest="variables",
        action="append",
        metavar="VAR=VAL",
        help="Define a variable binding (e.g., -v x=10 -v rate=0.05)",
    )

    # Output formatting
    parser.add_argument(
        "-r", "--raw",
        action="store_true",
        help="Print raw unadorned numeric output only (ideal for scripting and piping)",
    )

    parser.add_argument(
        "-c", "--card",
        action="store_true",
        help="Render styled terminal box card",
    )

    parser.add_argument(
        "-p", "--precision",
        type=int,
        default=6,
        help="Number of decimal places for float results (default: 6)",
    )

    parser.add_argument(
        "--list-funcs",
        action="store_true",
        help="List all supported math functions and constants",
    )

    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start an interactive math REPL session",
    )

    return parser


def parse_variables(var_list: Optional[List[str]]) -> dict:
    variables = {}
    if not var_list:
        return variables
    for item in var_list:
        if "=" not in item:
            raise ValueError(f"Variable definition must be in KEY=VALUE format, got '{item}'")
        k, v = item.split("=", 1)
        k = k.strip()
        v = v.strip()
        # Evaluate variable value as float or int
        try:
            val = int(v) if v.isdigit() or (v.startswith("-") and v[1:].isdigit()) else float(v)
        except ValueError:
            # Let the math evaluator calculate the variable value
            evaluator = MathEvaluator()
            val = evaluator.eval(v)
        variables[k] = val
    return variables


def run_repl():
    """Interactive calculation prompt."""
    print("\033[1;36mevalx\033[0m interactive calculator (type \033[1mexit\033[0m or \033[1mq\033[0m to quit)")
    evaluator = MathEvaluator()
    last_result = None

    while True:
        try:
            line = input("\033[1;34mevalx > \033[0m").strip()
            if not line:
                continue
            if line.lower() in ("exit", "quit", "q"):
                break
            if line.lower() == "clear":
                print("\033[H\033[J", end="")
                continue
            if line.startswith("let "):
                # Variable assignment: let x = 5
                parts = line[4:].split("=", 1)
                if len(parts) == 2:
                    k = parts[0].strip()
                    val = evaluator.eval(parts[1].strip())
                    evaluator.set_variable(k, val)
                    print(f"\033[90m{k} = {format_result(val)}\033[0m")
                    continue

            # Support 'ans' variable
            if last_result is not None:
                evaluator.set_variable("ans", last_result)

            res = evaluator.eval(line)
            last_result = res
            print(f"\033[1;32m= {format_result(res)}\033[0m")
        except (KeyboardInterrupt, EOFError):
            print()
            break
        except Exception as e:
            print(f"\033[1;31mError:\033[0m {e}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_funcs:
        print("\033[1;36mSupported Functions:\033[0m")
        funcs = sorted(MATH_FUNCTIONS.keys())
        for i in range(0, len(funcs), 6):
            print("  " + "  ".join(f"{f:10}" for f in funcs[i:i+6]))
        print("\n\033[1;36mSupported Constants:\033[0m")
        for k, v in MATH_CONSTANTS.items():
            print(f"  {k:6} = {v}")
        return 0

    if args.interactive or (not args.expr_flag and not args.positional_expr and sys.stdin.isatty()):
        run_repl()
        return 0

    # Combine expression tokens from either -e or positional arguments
    expr_tokens = []
    if args.expr_flag:
        expr_tokens.extend(args.expr_flag)
    if args.positional_expr:
        expr_tokens.extend(args.positional_expr)

    # Check if input piped from stdin
    if not expr_tokens and not sys.stdin.isatty():
        piped_content = sys.stdin.read().strip()
        if piped_content:
            expr_tokens = [piped_content]

    if not expr_tokens:
        parser.print_help()
        return 1

    expression = " ".join(expr_tokens)

    try:
        variables = parse_variables(args.variables)
    except Exception as e:
        print(f"\033[1;31mVariable Error:\033[0m {e}", file=sys.stderr)
        return 1

    evaluator = MathEvaluator(variables=variables)

    try:
        result = evaluator.eval(expression)
    except EvaluationError as e:
        print(f"\033[1;31mError:\033[0m {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\033[1;31mEvaluation Error:\033[0m {e}", file=sys.stderr)
        return 1

    if args.raw:
        # Machine-readable output for shell scripting: evalx -r '10 * 5'
        if isinstance(result, float) and result.is_integer():
            print(int(result))
        else:
            print(result)
    elif args.card:
        print(render_card(expression, result, variables))
    else:
        # Clean default output with result highlighting
        print(f"\033[1;32m{format_result(result, precision=args.precision)}\033[0m")

    return 0


if __name__ == "__main__":
    sys.exit(main())
