"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from importlib.metadata import version

try:
    __version__ = version(__name__)
except Exception as e:
    raise e

from ifpd import bioext, exception, query, stats
from ifpd import sections

__all__ = ["__version__", "bioext", "exception", "query", "sections", "stats"]
