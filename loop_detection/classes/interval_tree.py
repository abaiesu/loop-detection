from loop_detection.classes.range import Range
from loop_detection.classes.combination import Combination
from loop_detection.classes.multifield import MultiField
from typing import Iterable, Union, List, Set


class Node:
    def __init__(self, point, intervals, axis=0):
        self.point = point
        self.intervals = intervals
        self.span = [float('inf'), -1]
        self.axis = axis
        self.left = None
        self.right = None

    def find_intersects(self, c, result=None):

        if result is None:
            result = set()

        if isinstance(c, Combination):
            combi = c.rule
        else:
            combi = c

        if isinstance(combi, Range):
            if combi.is_member(self.point):
                result.update(self.intervals)
            elif combi.start <= self.span[1] and combi.end >= self.span[0]:  # if the combi is included in the span
                for to_check in self.intervals:  # check for each
                    if (to_check.rule & combi).empty_flag == 0:  # non-empty intersection
                        result.add(to_check)

            # now we explore left or right
            if combi.start < self.point and self.left:
                self.left.find_intersects(combi, result)
            if combi.end > self.point and self.right:
                self.right.find_intersects(combi, result)

        if isinstance(combi, MultiField):
            combi_axis = combi.rules[self.axis]
            if combi_axis.is_member(self.point):
                result.update(self.intervals)
            elif combi_axis.start <= self.span[1] and combi_axis.end >= self.span[
                0]:  # if the combi is included in the span
                for to_check in self.intervals:
                    if ((to_check.rule.rules[self.axis]) & combi_axis).empty_flag == 0:  # non-empty intersection
                        result.add(to_check)

            # now we explore left or right
            if combi_axis.start < self.point and self.left:
                self.left.find_intersects(combi, result)
            if combi_axis.end > self.point and self.right:
                self.right.find_intersects(combi, result)

        return result

    def add_to_tree(self, to_add):

        if isinstance(to_add, Combination):
            inter = to_add.rule
        else:
            inter = to_add

        if isinstance(inter, Range):
            if inter.is_member(self.point):
                self.intervals.add(to_add)
                if inter.start < self.span[0]:  # we start earlier
                    self.span[0] = inter.start
                if inter.end > self.span[1]:  # we start later
                    self.span[1] = inter.end
            elif self.left and inter.start < self.point:
                self.left.add_to_tree(to_add)
            elif self.right and inter.end > self.point:
                self.right.add_to_tree(to_add)

        if isinstance(inter, MultiField):
            inter_axis = inter.rules[self.axis]
            if inter_axis.is_member(self.point):
                self.intervals.add(to_add)
                if inter_axis.start < self.span[0]:  # we start earlier
                    self.span[0] = inter_axis.start
                if inter_axis.end > self.span[1]:  # we start later
                    self.span[1] = inter_axis.end
            elif self.left and inter_axis.start < self.point:
                self.left.add_to_tree(to_add)
            elif self.right and inter_axis.end > self.point:
                self.right.add_to_tree(to_add)

    def remove_from_tree(self, to_remove):

        if isinstance(to_remove, Combination):
            inter = to_remove.rule
        else:
            inter = to_remove

        if isinstance(inter, Range):
            if inter.is_member(self.point):
                self.intervals.remove(to_remove)
                if len(self.intervals) == 0:  # empty node
                    self.span = [float('inf'), -1]
                else:
                    starts = [interval.rule.start for interval in self.intervals]
                    ends = [interval.rule.end for interval in self.intervals]
                    self.span = [min(starts), max(ends)]
            elif self.left and inter.start < self.point:
                self.left.remove_from_tree(to_remove)
            elif self.right and inter.end > self.point:
                self.right.remove_from_tree(to_remove)

        if isinstance(inter, MultiField):
            inter_axis = inter.rules[self.axis]
            if inter_axis.is_member(self.point):
                self.intervals.remove(to_remove)
                if len(self.intervals) == 0:  # empty node
                    self.span = [float('inf'), -1]
                starts = [interval.rule.rules[self.axis].start for interval in self.intervals]
                ends = [interval.rule.rules[self.axis].end for interval in self.intervals]
                self.span = [min(starts), max(ends)]
            elif self.left and inter_axis.start < self.point:
                self.left.remove_from_tree(to_remove)
            elif self.right and inter_axis.end > self.point:
                self.right.remove_from_tree(to_remove)


def build_interval_tree(intervals: List,
                        keep_empty=False, axis=0, endpoints=None):
    """
    Stores the intervals in the input collection in an interval tree

    Parameters
    ---------
    intervals : Set[Union[Range, MultiField]]
        Collection of intervals
    keep_empty : bool, default = False
        If true, will build the skeleton of the tree, without adding intervals at the nodes/leaves
    axis : int, default = 0
        The axis along which to store the intervals (relevant if the intervals are Multifields)
    endpoints : List[int], default = None
        Used for induction

    Returns
    -------
    Node

    """

    if endpoints is None:
        starts = []
        ends = []
        if isinstance(intervals[0], Range):
            for inter in intervals:
                starts.append(inter.start)
                ends.append(inter.end)
        elif isinstance(intervals[0], MultiField):
            for inter in intervals:
                starts.append(inter.rules[axis].start)
                ends.append(inter.rules[axis].end)
        endpoints = sorted(set(starts + ends))

    if len(endpoints) != 0:
        # Find the middle point
        mid = len(endpoints) // 2
        mid_point = endpoints[mid]

        if keep_empty:
            root = Node(mid_point, set(), axis)
            root.left = build_interval_tree([], keep_empty, axis, endpoints[:mid])
            root.right = build_interval_tree([], keep_empty, axis, endpoints[mid + 1:])
            return root
        else:
            if isinstance(intervals[0], Range):
                mid_point_intervals = {interval for interval in intervals if interval.is_member(mid_point)}
                root = Node(mid_point, mid_point_intervals, axis)

            elif isinstance(intervals[0], MultiField):
                mid_point_intervals = {interval for interval in intervals if interval.rules[axis].is_member(mid_point)}
                root = Node(mid_point, mid_point_intervals, axis)
            else:
                raise ValueError("Trees are build for Ranges or Multifields with Range rules only")

            # Recursively build left and right subtrees
            new_intervals = [inter for inter in intervals if inter not in mid_point_intervals]
            root.left = build_interval_tree(new_intervals, keep_empty, axis, endpoints[:mid])
            root.right = build_interval_tree(new_intervals, keep_empty, axis, endpoints[mid + 1:])

            return root
