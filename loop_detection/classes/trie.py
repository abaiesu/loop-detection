from loop_detection.classes.wildcardexpr import WildcardExpr
from loop_detection.classes.combination import Combination
from loop_detection.classes.multifield import MultiField


class Trie:

    def __init__(self, key, depth, l, expr = None, left = None, middle = None, right = None):
        self.key = key
        self.exprs = set() #none for everything except leaves
        self.depth = depth
        self.left = left
        self.middle = middle
        self.right = right
        self.len = l

    def add_to_tree(self, expr, curr_expr = None, check = False):

        if not check:
            if isinstance(expr, WildcardExpr):
                curr_expr = expr.expr
            if isinstance(expr, Combination):
                if isinstance(expr.rule, WildcardExpr):
                    curr_expr = expr.rule.expr
                if isinstance(expr.rule, MultiField): #there is at most 1 wc
                    for r in expr.rule.rules:
                        if isinstance(r, WildcardExpr):
                            curr_expr = r.expr
                            break


            if len(curr_expr) == self.len - 1:
                check = True
            else:
                raise ValueError("The string isn't at the good length")

        if check:

            if len(curr_expr) == 0:
                self.exprs.add(expr)

            else:
                if curr_expr[0] == '0':
                    if not self.left:
                        self.left = Trie(key='0', depth= self.depth + 1, l=self.len)
                    self.left.add_to_tree(expr, curr_expr[1:], check = True)

                elif curr_expr[0] == '1':
                    if not self.middle:
                        self.middle = Trie(key='1', depth= self.depth + 1, l=self.len)
                    self.middle.add_to_tree(expr, curr_expr[1:], check = True)

                elif curr_expr[0] == '*':
                    if not self.right:
                        self.right = Trie(key='*', depth= self.depth + 1, l=self.len)
                    self.right.add_to_tree(expr, curr_expr[1:], check = True)


    def remove_from_tree(self, expr, curr_expr=None, check=False):

        if not check:
            if isinstance(expr, WildcardExpr):
                curr_expr = expr.expr
            if isinstance(expr, Combination):
                if isinstance(expr.rule, WildcardExpr):
                    curr_expr = expr.rule.expr
                if isinstance(expr.rule, MultiField): #there is at most 1 wc
                    for r in expr.rule.rules:
                        if isinstance(r, WildcardExpr):
                            curr_expr = r.expr
                            break
            if len(curr_expr) == self.len - 1:
                check = True
            else:
                raise ValueError("The string isn't at the correct length")

        if check:
            if len(curr_expr) == 0:
                self.exprs.remove(expr)
            else:
                next_char = curr_expr[0]
                if next_char == '0' and self.left:
                    self.left.remove_from_tree(expr, curr_expr[1:], check=True)
                    if not self.left.has_children() and len(self.left.exprs) == 0:
                        self.left = None
                elif next_char == '1' and self.middle:
                    self.middle.remove_from_tree(expr, curr_expr[1:], check=True)
                    if not self.middle.has_children() and len(self.middle.exprs) == 0: #no children and nothing stored
                        self.middle = None
                elif next_char == '*' and self.right:
                    self.right.remove_from_tree(expr, curr_expr[1:], check=True)
                    if not self.right.has_children() and len(self.right.exprs) == 0: #no children and nothing stored
                        self.right = None


    def has_children(self):
        return self.left is not None or self.middle is not None or self.right is not None


    def print_tree(self):
        self._print_tree_helper(self)


    def _print_tree_helper(self, node, indent=0, info = ''):
        if node is not None:
            print("  " * indent + info+ f" Key: {node.key}, Depth: {node.depth}, Expr: {node.exprs}")
            self._print_tree_helper(node.left, indent + 1, info = 'Left')
            self._print_tree_helper(node.middle, indent + 1, info = 'Middle')
            self._print_tree_helper(node.right, indent + 1, info = 'Right')

    def find_intersects(self, input_str, index=0):

        result = set()

        if isinstance(input_str, WildcardExpr):
            input_str = input_str.expr
        elif isinstance(input_str, Combination):
            if isinstance(input_str.rule, WildcardExpr):
                input_str = input_str.rule.expr
            elif isinstance(input_str.rule, MultiField): #there is at most 1 wc
                for r in input_str.rule.rules:
                    if isinstance(r, WildcardExpr):
                        input_str = r.expr
                        break

        if index == len(input_str):
            result.update(self.exprs)
            return result

        current_char = input_str[index]

        if current_char == '*':
            if self.left:
                result.update(self.left.find_intersects(input_str, index + 1))
            if self.middle:
                result.update(self.middle.find_intersects(input_str, index + 1))
            if self.right:
                result.update(self.right.find_intersects(input_str, index + 1))

        elif current_char == '0':
            if self.left:
                result.update(self.left.find_intersects(input_str, index + 1))

            if self.right:
                result.update(self.right.find_intersects(input_str, index + 1))

        elif current_char == '1':

            if self.middle:
                result.update(self.middle.find_intersects(input_str, index + 1))

            if self.right:
                result.update(self.right.find_intersects(input_str, index + 1))

        return result
