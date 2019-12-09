from pycparser import parse_file, c_generator, c_ast, c_parser

def check_structure(node):
    if isinstance(node, c_ast.FuncDef):
        body = node.body
        name = node.decl.name
        result = True
        result = result and check_single_return(body, name)
        result = result and check_loops(body, name)
        return result



def check_loops(node, function_name):
    #check whether the function contains jump statement or early exits
    LC = LoopChecker()
    if (not LC.checkLoopStructure(node)):
        print("%s violates single entry single exit contract" % function_name)
        return False
    return True


def check_single_return(node, function_name):
    #check whether the function contains a single return, the only exception is for IF-THEN-ELSE statement
    RH = ReturnHunter()
    num = RH.num_return(node)
    if num > 1:
        print("%s violates single return contract" % function_name)
        return False

    return True

class LoopChecker(c_ast.NodeVisitor):
    def __init__(self):
        self.result = True

    def checkLoopStructure(self, node):
        self.visit(node)
        return self.result

    def visit_Goto(self, node):
        if isinstance(node, c_ast.Goto):
            self.result=False
            return

    def visit_Break(self, node):
        if isinstance(node, c_ast.Break):
            self.result=False
            return

    def visit_Continue(self, node):
        if isinstance(node, c_ast.Continue):
            self.result=False
            return

    def visit_For(self, node):
        if isinstance(node, c_ast.For):
            RH = ReturnHunter()
            if (RH.num_return(node.stmt)) > 0:
                self.result=False
                return
            self.generic_visit(node)

    def visit_While(self, node):
        if isinstance(node, c_ast.While):
            RH = ReturnHunter()
            if (RH.num_return(node.stmt)) > 0:
                self.result = False
                return
            self.generic_visit(node)





class ReturnHunter(c_ast.NodeVisitor):
    def __init__(self):
        self.temp_container = []

    def num_return(self, node):
        if node is not None:
            self.visit(node)
            return len(self.temp_container)
        else:
            return 0


    def visit_Return(self,node):
        if isinstance(node, c_ast.Return):
            self.temp_container.append(node)

    def visit_If(self, node):
        if isinstance(node, c_ast.If):
            RH_then = ReturnHunter()
            RH_else = ReturnHunter()
            then_returns = RH_then.num_return(node.iftrue)
            else_returns = RH_else.num_return(node.iffalse)
            if then_returns <= 1 and else_returns <= 1 and then_returns+else_returns > 1:
                self.temp_container.append(node)
            else:
                self.temp_container+=RH_then.temp_container
                self.temp_container+=RH_else.temp_container
