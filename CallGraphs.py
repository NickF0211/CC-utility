import argparse
from os import path
from pycparser import parse_file, c_generator, c_ast, c_parser
from copy import *
from DataTypeAnalyzer import *
from StructureAnalyzer import *


reachable_recursion = False
reachable_functions = set()
illegal_types = False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--new', type=str, dest='new', default="new.c", help="new source file")
    parser.add_argument('--old', type=str, dest='old', default="old.c", help="old source file")
    parser.add_argument('--client', type=str, dest='client', default="client", help="client function name")
    parser.add_argument('--lib', type=str, dest='lib', default="lib", help="lib function name")

    args = parser.parse_args()
    path_old = args.old
    path_new = args.new

    if path.isfile(path_old) and path.isfile(path_new):
        trace_program_structure(path_old, path_new, args.client, args.lib)
    else:
        print("one of the input files doesn't exist")


def trace_program_structure (path_old, path_new, client, lib):
    old_ast = parse_file(path_old, use_cpp=True,
                         cpp_path='gcc',
                         cpp_args=['-E', r'-Iutils/fake_libc_include'])
    new_ast = parse_file(path_new, use_cpp=True,
                         cpp_path='gcc',
                         cpp_args=['-E', r'-Iutils/fake_libc_include'])

    #Pass one, analyze call graph and determine the recursion structure
    trace_tree = TraceFinder(old_ast, lib)
    trace_tree.print_trace(client=client)

    if (reachable_recursion):
        print("Exists reachable recursive call paths")
        #return

    #Pass two, analyze all functions on the call paths for well-structuredness and type constraint
    for func in reachable_functions:
        result = analyze_types(func, old_ast)


def analyze_types(func, file_node):
    FLU = funcDefLookUp()
    func_node = FLU.look_up(file_node, func)
    check_contract(func_node)
    check_structure(func_node)
    #print(func_node)
    return True




def TraceFinder(node, target):
    root = TreeNode(target)
    working_list=[root]
    while len(working_list) > 0:
        item = working_list.pop()
        LPF = LibPathFinder()
        LPF.find_target(node, item)
        updated_component = LPF.temp_container
        working_list += updated_component

    return root



class TreeNode():
    def __init__(self, value):
        self.value = value
        self.parent = None
        self.children = []
        self.recursive_trace =[]

    def add_child(self, value):
        if not self.is_recusive(value):
            child_node = TreeNode(value)
            self.children.append(child_node)
            child_node.parent = self
            return child_node


    def is_recusive(self, value):
        trace =  self._is_recursive(value, [value])
        if len(trace) == 0:
            return False
        else:
            trace.reverse()
            #print("recursive trace : " + " <- ".join(trace))
            self.recursive_trace.append([self.value] + trace[:-1])
            return True


    def _is_recursive(self, value, trace):
        trace.append(self.value)
        if self.value == value:
            return trace
        else:
            if self.parent is not None:
                return self.parent._is_recursive(value, trace)
            else:
                return []

    def get_value(self):
        return self.value

    def print_trace(self, client=None):
        self._print_trace([], client=client)

    def _print_trace(self, anestor, client=None, C_recusion=True, recursive_trace=False):
        global reachable_recursion
        global reachable_functions

        if C_recusion and len(self.recursive_trace) > 0:
            #consider base case
            self._print_trace( deepcopy(anestor), client=client, C_recusion=False, recursive_trace=recursive_trace)
            #consider all recursive cases
            for r_t in self.recursive_trace:
                local_acestor = deepcopy(anestor)
                local_acestor.append( "( " + " <- ".join(r_t) + " )*")
                self._print_trace(local_acestor, client=client, C_recusion=False, recursive_trace=True)
        else:
            anestor.append(self.get_value())
            if len(self.children) == 0:
                if (client is None or client in anestor):
                    if (not recursive_trace):
                        print ( "Reachable Trace: " + " <- ".join(anestor))
                        for func in anestor:
                            reachable_functions.add(func)
                    else:
                        print("Recursive reachable Trace: " + " <- ".join(anestor))
                        reachable_recursion = True

            else:
                for node in self.children:
                    local_acestor =deepcopy(anestor)
                    node._print_trace(local_acestor, client=client, recursive_trace = recursive_trace)



class LibPathFinder(c_ast.NodeVisitor):
    def __init__(self):
        self.target = None
        self.parent_child = {}
        self.temp_container = []

    def find_target(self, node, target):
        self.target=target
        self.visit(node)

    def generic_visit(self, node):
        """ Called if no explicit visitor function exists for a
            node. Implements preorder visiting of the node.
        """
        for c in node:
            self.parent_child[c] = node
            self.visit(c)

    def visit_FuncCall(self, node):
        if isinstance(node, c_ast.FuncCall):
            if (node.name.name == self.target.get_value()):
                #find the target, now look for its host function
                while not (isinstance(node, c_ast.FileAST)):
                    # stop until the file node in case nested function decl
                    if (isinstance(node, c_ast.FuncDef)):
                        c_Tnode = self.target.add_child(node.decl.name)
                        if c_Tnode is not None:
                            self.temp_container.append(c_Tnode)
                    node = self.parent_child[node]
                #Now try to find the located function def


class funcDefLookUp(c_ast.NodeVisitor):
    def __index__(self):
        self.target = None
        self.container = None

    def look_up(self, node, target):
        self.target = target
        self.visit(node)
        result = self.container
        self.target = None
        self.container = None
        return  result

    def visit_FuncDef(self,node):
        if isinstance(node, c_ast.FuncDef):
            if (node.decl.name == self.target):
                self.container = node

if __name__ == '__main__':
    main()
