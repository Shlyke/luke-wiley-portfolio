# Mini Bash Shell

A simplified Bash-like shell implemented in C, supporting core shell functionality including built-in commands, command parsing, control operators, and I/O redirection.  
Developed for CMPSC 473: Operating Systems at Penn State.

---

## Features

- Built-in support for `cd`, `pwd`, `exit`, and `quit`
- Execution of arbitrary commands via `fork()` and `execvp()`
- Support for environment variables (`$VAR`)
- Full operator support:
  - Sequential: `;`
  - Parallel: `&`
  - Conditional: `&&`, `||`
  - Piping: `|`
- I/O Redirection:
  - `>`, `<`, `>>`, `2>`, `2>>`, `&>`
- Parser implemented using Flex/Bison via `parser.l` and `parser.y`

---

## File Overview

- `main.c` – Shell entry point and command loop
- `cmd.c`, `cmd.h` – Execution logic for commands and operators
- `utils.c`, `utils.h` – Helper functions for environment, redirection, etc.
- `parser.l`, `parser.y`, `parser.h` – Lex/Yacc-based input parser
- `Makefile` – Builds the shell binary

---

### Compile
```bash
make
