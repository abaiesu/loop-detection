"""Top-level package for Loop Detection."""

__author__ = """Antonia Baies"""
__email__ = 'baies.antonia@gmail.com'
__version__ = '0.1.1'


from loop_detection.classes.rule import Rule
from loop_detection.classes.range import Range
from loop_detection.classes.wildcardexpr import WildcardExpr
from loop_detection.classes.multifield import MultiField
from loop_detection.algo.uc_algo import get_UC
from loop_detection.loop_detection_code import loop_detection
