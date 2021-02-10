"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from ifpd.const import __version__
from ifpd.scripts import arguments as ap
from ifpd import scripts
import sys


def default_parser(*args) -> None:
    print("ifpd -h for usage details.")
    sys.exit()


def main():
    parser = argparse.ArgumentParser(
        description=f"""
Version:    {__version__}
Author:     Gabriele Girelli
Docs:       http://ggirelli.github.io/ifish-probe-design
Code:       http://github.com/ggirelli/ifish-probe-design

An iFISH probe design pipeline, with web interface included.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.set_defaults(parse=default_parser)
    parser = ap.add_version_option(parser)

    subparsers = parser.add_subparsers(
        title="sub-commands",
        help="Access the help page for a sub-command with: sub-command -h",
    )

    scripts.dbchk.init_parser(subparsers)
    scripts.mkdb.init_parser(subparsers)
    scripts.query.query.init_parser(subparsers)
    scripts.serve.init_parser(subparsers)

    args = parser.parse_args()
    args = args.parse(args)
    args.run(args)
