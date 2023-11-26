"""Top-level package for Loop Detection."""

__author__ = """Antonia Baies"""
__email__ = 'baies.antonia@gmail.com'
__version__ = '0.1.0'


from loop_detection.set_rep.rule import Rule
from loop_detection.set_rep.range import Range
from loop_detection.set_rep.wildcardexpr import WildcardExpr
from loop_detection.set_rep.multifield import MultiField

from loop_detection.algo.uc_algo import get_UC
