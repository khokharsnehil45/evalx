# evalx (calc / mathx)

A fast, safe, zero-dependency mathematical expression evaluator and terminal calculator.

> **Note on naming**: In standard Linux/macOS shells (`bash`, `zsh`), `eval` is a reserved built-in keyword. Therefore, this tool is packaged as **`evalx`**, and also aliases cleanly to **`calc`** and **`mathx`**.

---

## ⚡ Quick Examples

```bash
# Your exact expression with -e
evalx -e 10 + 20 - '(10 * 2)'
# Output: 10

# Direct positional expression
evalx '10 + 20 - (10 * 2)'

# With pretty terminal card view (-c)
evalx -c '10 + 20 - (10 * 2)'
```

Output:
```
╭────────────────────────────────────╮
│  EVALX CALCULATOR                  │
├────────────────────────────────────┤
│ Expr   : 10 + 20 - (10 * 2)        │
├────────────────────────────────────┤
│ Result : 10                        │
│ Repr   : hex: 0xa  |  bin: 0b1010  │
╰────────────────────────────────────╯
```

---

## 🚀 Features

- **Safe AST Evaluation**: Parses mathematical syntax trees directly via Python's AST. Never uses unsafe `eval()`.
- **Zero Runtime Dependencies**: Uses Python standard library only.
- **Natural Math Powers**: Supports both `2^8` and `2**8` (yields `256`).
- **Rich Math Functions & Constants**: Includes `sqrt`, `cbrt`, `sin`, `cos`, `tan`, `log`, `log10`, `factorial`, `gcd`, `pi`, `e`, `tau`.
- **Variable Bindings**: Pass `-v x=10 -v y=5` to evaluate expressions with parameters.
- **Pipe & Scripting Ready**: Pass `-r` / `--raw` for unadorned numeric values or pipe via `stdin`.
- **Interactive REPL**: Run `evalx` with no arguments to launch an interactive math shell.

---

## 🛠 Usage

### 1. Variables
```bash
evalx 'x^2 + 2*x + 1' -v x=5
# Output: 36
```

### 2. Math Functions & Trigonometry
```bash
evalx 'sin(pi / 4) + sqrt(16)'
# Output: 4.707107

evalx 'factorial(6) / fact(3)'
# Output: 120
```

### 3. Piping & Shell Scripts
```bash
echo "100 * 45 - 250" | evalx -r
# Output: 4250
```

### 4. Interactive REPL Mode
```bash
evalx -i
# or simply:
evalx
```
```text
evalx > let x = 100
x = 100
evalx > x * 2.5
= 250
evalx > ans + 50
= 300
evalx > exit
```

---

## 📦 Installation

```bash
git clone https://github.com/khokharsnehil45/evalx.git
cd evalx
pip install -e .
```

Installs `evalx`, `calc`, and `mathx` commands.
