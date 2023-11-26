# -*- coding: utf-8 -*-
"""
Copyright Antonia Baies
baies.antonia@gmail.com

This file is part of Loop Detection.
"""

from loop_detection.set_rep.rule import Rule
from loop_detection.set_rep.range import Range


class MultiField(Rule):
    """
    Class for multifield rule representation (n-tuples)

    Attributes
    ----------
    rules : list
        list of rules for each field
        items can be Range or WildcardExpr instances

    Examples
    --------
        >>> r1 = MultiField([Range((10, 20)), Range((1, 3))])
        >>> r2 = MultiField([Range((5, 15)), Range((1, 1))])
        >>> r1 & r2
        [10, 15], [1, 1]
        >>> MultiField([Range((10, 15)), Range((1, 1))]) < r1
        True
        >>> r1.get_card()
        33

    """

    def __init__(self, rules):
        super().__init__(rules, float('inf'), field=None)
        self.rules = rules  # rules is a list of Rule instances
        if rules is not None:
            for rule in rules:
                if rule.empty_flag:
                    self.empty_flag = 1
        if not self.empty_flag:
            result = 1
            for rule in self.rules:
                result *= rule.get_card()
            self.card = result

    def pretty_print(self):

        """Print the rules with a field per line, with the name of the field"""

        rule_reprs = [
            f'Field {i + 1}: {repr(rule)}, {rule.__class__.__name__}, card = {rule.get_card()}' if rule.field is None
            else f'{rule.field}: {repr(rule)}, {rule.__class__.__name__}, card = {rule.get_card()}' for i, rule in
            enumerate(self.rules)]
        print('\n'.join(rule_reprs))

    def __repr__(self):
        string = ''
        for i, rule in enumerate(self.rules):
            string += repr(rule)
            if i != len(self.rules) - 1:
                string += ', '
        return string

    def __and__(self, other):

        """
        Returns the result of set intersection

        Parameters
        ---------
        other : MultiField
        """

        if self.empty_flag | other.empty_flag:  # one of the sets is empty
            return MultiField(None)
        intersections = []
        for rule, other_rule in zip(self.rules, other.rules):
            intersection = rule & other_rule
            if intersection.empty_flag:  # if any intersection is empty, then the whole intersection is empty
                return MultiField(None)
            intersections.append(intersection)
        return MultiField(intersections)

    def __lt__(self, other):

        """
        Check if self is included in other (equality is accepted)

        Parameters
        ---------
        other : MultiField

        Returns
        -------
        bool
        """

        bools = [rule1 < rule2 for rule1, rule2 in zip(self.rules, other.rules)]
        return all(bools)  # bool_1 & bool_2 & ... & bool_n

    def __eq__(self, other):
        bools = [rule1 == rule2 for rule1, rule2 in zip(self.rules, other.rules)]
        return all(bools)  # bool_1 & bool_2 & ... & bool_n

    def __hash__(self):
        hash_values = tuple(hash(rule) for rule in self.rules)
        return hash(hash_values)

    def is_member(self, point):
        bools = [field.is_member(coord) for coord, field in zip(point, self.rules)]
        return all(bools)  # bool_1 & bool_2 & ... & bool_n

    def get_card(self):
        return self.card



