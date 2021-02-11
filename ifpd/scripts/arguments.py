"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from ifpd.const import __version__
import logging
import sys


def add_version_option(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument(
        "--version", action="version", version=f"{sys.argv[0]} {__version__}"
    )
    return parser


def check_n_oligo(args, selectCondition):
    assert 0 < selectCondition.sum(), "".join(
        [
            "no oligos found in the specified region.",
            f" [{args.chrom}:{args.region[0]}-{args.region[1]}]",
        ]
    )
    if args.exact_n_oligo:
        assert args.n_oligo <= selectCondition.sum(), "".join(
            [
                "there are not enough oligos in the database.",
                f" Asked for {args.n_oligo}, {selectCondition.sum()} found.",
            ]
        )
    elif args.n_oligo > selectCondition.sum():
        logging.info(
            "".join(
                [
                    f"Found {selectCondition.sum()} oligos in",
                    f" {args.chrom}:{args.region[0]}-{args.region[1]}",
                ]
            )
        )
        logging.warning(
            "".join(
                [
                    f"Designing a probe with {selectCondition.sum()} oligos",
                    f" (instead of {args.n_oligo}).",
                ]
            )
        )
        args.n_oligo = selectCondition.sum()
    return args
