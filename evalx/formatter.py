"""Formatting and terminal styling for evalx results."""

from typing import Union


def format_result(val: Union[int, float, complex], precision: int = 6) -> str:
    """Format numerical result cleanly (omit trailing .0 if integer)."""
    if isinstance(val, (int, float)):
        if isinstance(val, float) and val.is_integer():
            return f"{int(val):,}"
        if isinstance(val, int):
            return f"{val:,}"
        # Float with precision
        formatted = f"{val:,.{precision}f}".rstrip("0").rstrip(".")
        return formatted
    return str(val)


def render_card(expression: str, result: Union[int, float, complex], variables: dict = None) -> str:
    """Render a clean terminal card with expression, breakdown, and result."""
    formatted_res = format_result(result)
    
    # Calculate box width
    expr_line = f"  Expr   :  {expression}"
    res_line = f"  Result :  {formatted_res}"
    
    var_lines = []
    if variables:
        vars_str = ", ".join(f"{k}={v}" for k, v in variables.items())
        var_lines.append(f"  Vars   :  {vars_str}")
        
    all_lines = [expr_line] + var_lines + [res_line]
    max_len = max(len(l) for l in all_lines)
    box_width = max(max_len + 4, 38)
    
    border = "─" * (box_width - 2)
    sep = "─" * (box_width - 2)
    
    out = []
    out.append(f"╭{border}╮")
    out.append(f"│  \033[1;36mEVALX CALCULATOR\033[0m{' ' * (box_width - 19)}│")
    out.append(f"├{sep}┤")
    out.append(f"│ \033[90mExpr   :\033[0m \033[1m{expression}\033[0m{' ' * (box_width - len(expression) - 12)}│")
    
    if variables:
        for vl in var_lines:
            content = vl.replace("  Vars   :  ", "")
            out.append(f"│ \033[90mVars   :\033[0m {content}{' ' * (box_width - len(content) - 12)}│")
            
    out.append(f"├{sep}┤")
    out.append(f"│ \033[1;32mResult :\033[0m \033[1;32m{formatted_res}\033[0m{' ' * (box_width - len(formatted_res) - 12)}│")
    
    # If integer, also show hex & binary representations
    if isinstance(result, (int, float)) and (isinstance(result, int) or result.is_integer()):
        int_val = int(result)
        if 0 <= int_val < 2**32:
            hex_str = f"hex: {hex(int_val)}  |  bin: {bin(int_val)}"
            out.append(f"│ \033[90mRepr   :\033[0m \033[90m{hex_str}\033[0m{' ' * (box_width - len(hex_str) - 12)}│")
            
    out.append(f"╰{border}╯")
    return "\n".join(out)
