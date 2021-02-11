"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from ifpd.const import __version__
import joblib  # type: ignore
import logging
from rich.logging import RichHandler  # type: ignore
from rich.console import Console  # type: ignore
import os
import sys
from typing import Optional


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


def add_log_file_handler(path: str, logger_name: Optional[str] = None) -> None:
    """Adds log file handler to logger.

    By defaults, adds the handler to the root logger.

    Arguments:
        path {str} -- path to output log file

    Keyword Arguments:
        logger_name {str} -- logger name (default: {""})
    """
    assert not os.path.isdir(path)
    log_dir = os.path.dirname(path)
    assert os.path.isdir(log_dir) or "" == log_dir
    fh = RichHandler(console=Console(file=open(path, mode="w+")), markup=True)
    fh.setLevel(logging.INFO)
    logging.getLogger(logger_name).addHandler(fh)
    logging.info(f"[green]Log to[/]: '{path}'")


def check_threads(threads: int) -> int:
    if threads > joblib.cpu_count():
        return joblib.cpu_count()
    elif threads <= 0:
        return 1
    return threads
