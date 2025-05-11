import ASTNodeDefs as AST
class Lexer:
    def __init__(self, code):
        self.code = code
        self.position = 0
        self.current_char = self.code[self.position]
        self.tokens = []
    
    # Move to the next position in the code increment by one.
    def advance(self):
        self.position += 1
        if self.position >= len(self.code):
            self.current_char = None
        else:
            self.current_char = self.code[self.position]

    # If the current char is whitespace, move ahead.
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    # Tokenize the identifier.
    def identifier(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return ('IDENTIFIER', result)
    

    # Tokenize numbers, including float handling
    def number(self):
        result = ''
        is_float = False
        #float can start with a num or '.', and must have num after '.'
        if self.current_char == '.':
            result += '.'
            self.advance()
            if self.current_char is None or not self.current_char.isdigit():
                raise ValueError(f" Invalid float number at position {self.position}")
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            is_float = True
        else:
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            if self.current_char == '.':
                result += '.'
                self.advance()
                if self.current_char is None or not self.current_char.isdigit():
                    raise ValueError(f" Invalid float number at position {self.position}")
                while self.current_char is not None and self.current_char.isdigit():
                    result += self.current_char
                    self.advance()
                is_float = True
        if is_float:
            return ('FNUMBER', float(result))
        else:
            return ('NUMBER', int(result))

    def token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isalpha():
                ident = self.identifier()
                if ident[1] == 'if':
                    return ('IF', 'if')
                elif ident[1] == 'else':
                    return ('ELSE', 'else')
                elif ident[1] == 'while':
                    return ('WHILE', 'while')
                elif ident[1] == 'int':
                    return ('INT', 'int')
                elif ident[1] == 'float':
                    return ('FLOAT', 'float')
                return ident  # Generic identifier
            if self.current_char.isdigit() or self.current_char == '.':
                return self.number()
            if self.current_char == '+':
                self.advance()
                return ('PLUS', '+')
            if self.current_char == '-':
                self.advance()
                return ('MINUS', '-')
            if self.current_char == '*':
                self.advance()
                return ('MULTIPLY', '*')
            if self.current_char == '/':
                self.advance()
                return ('DIVIDE', '/')
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return ('EQ', '==')
                return ('EQUALS', '=')
            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return ('NEQ', '!=')
            if self.current_char == '<':
                self.advance()
                return ('LESS', '<')
            if self.current_char == '>':
                self.advance()
                return ('GREATER', '>')
            if self.current_char == '(':
                self.advance()
                return ('LPAREN', '(')
            if self.current_char == ')':
                self.advance()
                return ('RPAREN', ')')
            if self.current_char == ',':
                self.advance()
                return ('COMMA', ',')
            if self.current_char == ':':
                self.advance()
                return ('COLON', ':')
            
            if self.current_char == '{':
                self.advance()
                return ('LBRACE', '{')
            if self.current_char == '}':
                self.advance()
                return ('RBRACE', '}')
            
            if self.current_char == '\n':
                self.advance()
                continue

            raise ValueError(f"Illegal character at position {self.position}: {self.current_char}")

        return ('EOF', None)

    # Collect all the tokens in a list.
    def tokenize(self):
        while True:
            token = self.token()
            self.tokens.append(token)
            if token[0] == 'EOF':
                break
        return self.tokens



import ASTNodeDefs as AST

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = tokens.pop(0)
        # Use these to track the variables and their scope
        self.symbol_table = {'global': {}}
        self.scope_counter = 0
        self.scope_stack = ['global']
        self.messages = []

    def error(self, message):
        self.messages.append(message)
    
    def advance(self):
        if self.tokens:
            self.current_token = self.tokens.pop(0)

    # TODO: Implement logic to enter a new scope, add it to symbol table, and update `scope_stack`
    def enter_scope(self):
        #must create new scope name, add to stack, and add to table
        self.scope_counter += 1
        current_scope = f'scope_{self.scope_counter}'
        self.scope_stack.append(current_scope)
        self.symbol_table[current_scope] = {}


    # TODO: Implement logic to exit the current scope, removing it from `scope_stack`
    def exit_scope(self):
        if self.current_scope() != 'global':
            self.scope_stack.pop()

    # Return the current scope name
    def current_scope(self):
        return self.scope_stack[-1]

    # TODO: Check if a variable is already declared in the current scope; if so, log an error
    def checkVarDeclared(self, identifier):
        if identifier in self.symbol_table[self.current_scope()]:
            self.error(f"Variable {identifier} has already been declared in the current scope")

    # TODO: Check if a variable is declared in any accessible scope; if not, log an error
    def checkVarUse(self, identifier):
        for scope in self.scope_stack:
            if identifier in self.symbol_table[scope]:
                return #found variable, useable in code
        self.error(f"Variable {identifier} has not been declared in the current or any enclosing scopes")

    # TODO: Check type mismatch between two entities; log an error if they do not match
    def checkTypeMatch2(self, vType, eType, var, exp):
        #check if operations between vType and eType are doable, must be the same
        if (vType == 'int' and eType == 'float') or (eType == 'int' and vType == 'float'):
            self.error(f"Type Mismatch between {vType} and {eType}")

    # TODO: Implement logic to add a variable to the current scope in `symbol_table`
    def add_variable(self, name, var_type):
        self.symbol_table[self.current_scope()][name] = var_type

    # TODO: Retrieve the variable type from `symbol_table` if it exists
    def get_variable_type(self, name):
        #iterate through most recent scopes and symbol tables to find var name
        for scope in reversed(self.scope_stack):
            if name in self.symbol_table[scope]:
                return self.symbol_table[scope][name]
        

    def parse(self):
        return self.program()

    def program(self):
        statements = []
        while self.current_token[0] != 'EOF':
            statements.append(self.statement())
        return AST.Block(statements)

    # TODO: Modify the `statement` function to dispatch to declare statement
    def statement(self):
        if self.current_token[0] == 'INT' or self.current_token[0] == 'FLOAT':
            return self.decl_stmt()
        elif self.current_token[0] == 'IDENTIFIER':
            if self.peek() == 'EQUALS':
                return self.assign_stmt()
            elif self.peek() == 'LPAREN':
                return self.function_call()
            else:
                raise ValueError(f"Unexpected token after identifier: {self.current_token}")
        elif self.current_token[0] == 'IF':
            return self.if_stmt()
        elif self.current_token[0] == 'WHILE':
            return self.while_stmt()
        else:
            raise ValueError(f"Unexpected token: {self.current_token}")

    # TODO: Implement the declaration statement and handle adding the variable to the symbol table
    def decl_stmt(self):
        #type > var > equals > value
        var_type = self.current_token[1]
        self.advance()

        if self.current_token[0] != 'IDENTIFIER':
            raise ValueError(f"Expected identifier after type, got {self.current_token}")
        var_name = self.current_token[1]
        self.checkVarDeclared(var_name)
        self.advance()
        if self.current_token[0] != 'EQUALS':
            raise ValueError(f"Expected '=' after type, got {self.current_token}")
        self.advance()
        expression = self.expression()
        self.checkTypeMatch2(var_type, expression.value_type, var_name, expression)
        self.add_variable(var_name, var_type)
        return AST.Declaration(var_type, var_name, expression)

    # TODO: Parse assignment statements, handle type checking
    def assign_stmt(self):
        ident = self.current_token
        var_name = ident[1]
        self.checkVarUse(var_name)
        var_type = self.get_variable_type(var_name)
        self.advance()
        self.expect('EQUALS')
        exp = self.expression()
        #match var and exp types
        self.checkTypeMatch2(var_type, exp.value_type, ident, exp)
        return AST.Assignment(var_name, exp)

    # TODO: Implement the logic to parse the if condition and blocks of code
    def if_stmt(self):
        self.advance()
        condition = self.boolean_expression()
        self.expect('LBRACE')
        self.enter_scope()
        then_block = self.block()
        self.exit_scope()
        self.expect('RBRACE')
        if self.current_token[0] == 'ELSE':
            self.advance()
            self.expect('LBRACE') #handles Advance
            self.enter_scope()
            else_block= self.block() #advances out of if_stmt
            self.exit_scope()
            self.expect('RBRACE')
        else:
            else_block = None
        return AST.IfStatement(condition, then_block, else_block)

    # TODO: Implement the logic to parse while loops with a condition and a block of statements
    def while_stmt(self):
        #While > Boolean > Colon > Block
        self.advance()
        condition = self.boolean_expression() #Handles advance
        self.expect('LBRACE') #handles Advance
        self.enter_scope()
        block = self.block() #handles Advance, body of while_stmt
        self.exit_scope()
        self.expect('RBRACE')
        return AST.WhileStatement(condition, block)

    # TODO: Implement logic to capture multiple statements as part of a block
    def block(self):
        statements = []
        while self.current_token[0] != 'EOF' and self.current_token[0] != 'RBRACE':
            statements += [self.statement()] #handles advancement
        return AST.Block(statements)

    # TODO: Implement logic to parse binary operations (e.g., addition, subtraction) with correct precedence and type checking
    def expression(self):
        """
        Parses an expression. Handles operators like +, -, etc.
        Example:
        x + y - 5
        TODO: Implement logic to parse binary operations (e.g., addition, subtraction) with correct precedence and type checking.
        """
        left = self.term()
        while self.current_token[0] in ['PLUS', 'MINUS']:
            op = self.current_token[0]
            self.advance()
            right = self.term()
            self.checkTypeMatch2(left.value_type, right.value_type, left, right)
            left = AST.BinaryOperation(left, op, right, value_type=left.value_type)

        return left

    # TODO: Implement parsing for boolean expressions and check for type compatibility
    def boolean_expression(self):
        left = self.expression()  
        while self.current_token[0] in ['EQ', 'NEQ', 'GREATER', 'LESS', 'LTE', 'GTE']:  
            op = self.current_token  
            self.advance()  
            right = self.expression()  
            self.checkTypeMatch2(left.value_type, right.value_type, left, right)
            left = AST.BooleanExpression(left, op, right)
        return left
        

    # TODO: Implement parsing for multiplication and division and check for type compatibility
    def term(self):
        left = self.factor()  
        while self.current_token[0] in ['MULTIPLY', 'DIVIDE']: 
            op = self.current_token[0]
            self.advance()  
            right = self.factor()  
            self.checkTypeMatch2(left.value_type, right.value_type, left, right)
            left = AST.BinaryOperation(left, op, right, value_type=left.value_type)
    
        return left
        
    def factor(self):
        if self.current_token[0] == 'NUMBER':
            num = self.current_token[1]
            self.advance()
            return AST.Factor(num, 'int')
        elif self.current_token[0] == 'FNUMBER':
            num = self.current_token[1]
            self.advance()
            return AST.Factor(num, 'float')
        elif self.current_token[0] == 'IDENTIFIER':
            # TODO: Ensure that you parse the identifier correctly, retrieve its type from the symbol table, and check if it has been declared in the current or any enclosing scopes.
            var_name = self.current_token[1]
            self.checkVarUse(var_name)
            var_type = self.get_variable_type(var_name)
            self.advance()
            return AST.Factor(var_name, var_type)
        elif self.current_token[0] == 'LPAREN':
            self.advance()
            expr = self.expression()
            self.expect('RPAREN')
            return expr
        else:
            raise ValueError(f"Unexpected token in factor: {self.current_token}")

    def function_call(self):
        func_name = self.current_token[1]
        self.advance()
        self.expect('LPAREN')
        args = self.arg_list()
        self.expect('RPAREN')

        return AST.FunctionCall(func_name, args)

    def arg_list(self):
        """
        Parses a list of function arguments.
        Example:
        (x, y + 5)
        """
        args = []
        if self.current_token[0] != 'RPAREN':
            args.append(self.expression())
            while self.current_token[0] == 'COMMA':
                self.advance()
                args.append(self.expression())

        return args

    def expect(self, token_type):
        if self.current_token[0] == token_type:
            self.advance()
        else:
            raise ValueError(f"Expected token {token_type}, but got {self.current_token[0]}")

    def peek(self):
        return self.tokens[0][0] if self.tokens else None
