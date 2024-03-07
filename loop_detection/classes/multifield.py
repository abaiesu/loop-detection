# -*- coding: utf-8 -*-
"""
Copyright Antonia Baies
baies.antonia@gmail.com

This file is part of Loop Detection.
"""

from loop_detection.classes import Rule, Range, WildcardExpr

class MultiField(Rule):
    """
    Class for multifield rule representation (n-tuples)

    Parameters
    ----------
    rules : list
        list of rules for each field, can be Range or WildcardExpr instances

    Attributes
    ----------
    rules : list
    card : int
        cardinality of the rule
    empty_flag : int
        1 if the rule is empty, 0 otherwise

    Examples
    --------
        >>> r1 = MultiField([Range(10, 20), Range(1, 3)])
        >>> r2 = MultiField([Range(5, 15), WildcardExpr("0**1")])

    """

    def __init__(self, rules, name = None, max_card = float('inf'), field = None):
        super().__init__(name, max_card, None)
        self.rules = rules  # rules is a list of Rule instances
        if rules is not None:
            count_empty_flags = 0
            for rule in rules:
                count_empty_flags += rule.empty_flag
            if count_empty_flags == 0: #if none are empty, then the multifield isn't empty
                self.empty_flag = 0
                #print('succ')

        #if self.empty_flag == 0:
                result = 1
                for rule in self.rules:
                    #print(rule.get_card(), rule)
                    result *= rule.get_card()
                self.card = result
                #print(result)

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

        Returns
        -------
        MultiField

        Examples
        --------
            >>> r1 = MultiField([Range(10, 20), Range(1, 3)])
            >>> r2 = MultiField([Range(5, 15), Range(1, 1)])
            >>> r1 & r2
            [10, 15], [1, 1]
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

        Examples
        --------
            >>> r1 = MultiField([Range(10, 20), Range(1, 3)])
            >>> r2 = MultiField([Range(13, 15), Range(1, 1)])
            >>> r2 < r1
            True
        """

        for rule1, rule2 in zip(self.rules, other.rules):
            if not (rule1 < rule2):
                return False
        return True

    def __eq__(self, other):


        for rule1, rule2 in zip(self.rules, other.rules):
            if rule1 != rule2:
               return False
        return True

    def __hash__(self):
        hash_values = tuple(hash(rule) for rule in self.rules)
        return hash(hash_values)

    def is_member(self, point):
        for coord, field in zip(point, self.rules):
            if not field.is_member(coord):
                return False
        return True

    def get_card(self):
        return self.card



