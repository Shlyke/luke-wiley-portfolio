# Python Parser Project

This project implements a custom lexer, parser, and type checker for a simple programming language using Python. It builds an Abstract Syntax Tree (AST) from input, checks for semantic and type errors, and validates code structure based on a defined grammar.

---

## Features

- **Custom Lexer**: Tokenizes identifiers, numbers, symbols, and keywords
- **Parser**: Builds an AST using recursive descent techniques
- **AST Nodes**: Represent declarations, assignments, operations, and control structures
- **Type Checking**: Validates assignments and expressions (e.g., int vs float)
- **Scope Management**: Tracks variable declarations and nesting rules
- **Error Reporting**: Detects and reports issues like redeclarations, mismatches, or undeclared variables
- **Test Framework**: Uses `verify.py` to compare test results against expected outputs

---

## How to Run

From inside the `python-parser` folder:

```bash
python verify.py
