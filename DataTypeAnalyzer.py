from pycparser import parse_file, c_generator, c_ast, c_parser

acceptable_type = {'int', 'void'}



def check_contract(node, forceCompliance=False):
    if isinstance(node, c_ast.FuncDef):
        # check return type
        funcDecl = node.decl
        Ftype = funcDecl.type
        if not check_type(Ftype,node):
            return False

        #check param types
        Ftype = node.decl
        while (not isinstance(Ftype, c_ast.FuncDecl)):
            Ftype = Ftype.type
            args = Ftype.args
            if (isinstance(args, c_ast.ParamList)):
                p_list = args.params
                for p in p_list:
                    if (not check_type(p, node)):
                        return False

        #check body decl's
        BTC = BodyTypeChecker(node)
        if not (BTC.checkType(node.body, forceCompliance=forceCompliance)):
            return False


def check_type(Ftype, node):
    while not isinstance(Ftype, c_ast.TypeDecl):
        if isinstance(Ftype, c_ast.PtrDecl):
            print("Error: %s's pointer return type is not supported" % node.decl.name)
            return False
        Ftype = Ftype.type
    output_type = Ftype.type.names
    if len(output_type) > 1 or not (output_type[0] in acceptable_type):
        print("Error: %s's invalid type: %s" % (node.decl.name, output_type))
        return False
    return True

class BodyTypeChecker(c_ast.NodeVisitor):
    def __init__(self, original_node):
        self.original_node = original_node
        self.result = True

    def checkType(self,node, forceCompliance=False):
        self.visit(node)
        return not forceCompliance or self.result

    def visit_PtrDecl(self):
        print("Error: %s's pointer return type is not supported" % self.original_node.decl.name)
        self.result = False

    def visit_TypeDecl(self, node):
        global acceptable_type
        output_type = node.type.names
        if len(output_type) > 1 or not (output_type[0] in acceptable_type):
            print("Error: %s's invalid type: %s" % (self.original_node.decl.name, output_type))
            self.result = False
