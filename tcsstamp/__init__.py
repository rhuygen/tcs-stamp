"""
TCS EGSE to STAMP Converter
"""

from .__version__ import __version__

from .sock_if import TCSInterface
from .sock_if import STAMPInterface
from .console import print_table
from .process import timestamp_key
