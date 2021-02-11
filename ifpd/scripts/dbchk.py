"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from ifpd import query
from ifpd.scripts import arguments as ap  # type: ignore
from ifpd.exception import enable_rich_assert
import logging
from rich.logging import RichHandler  # type: ignore

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)


def init_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        __name__.split(".")[-1],
        description="""
Checks integrity of a database. Specifically:
- a ".config" file must be present
    * Overlapping status must match.
- At least one non-empty chromosome file
    * Appropriate format (3 columns).
    * Positions must be sorted.
    * An ODN must end after it starts.
    * No ODNs can start from the same position.
    * No ODNs can be totally included in another one.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Check integrity of a database.",
    )

    parser.add_argument(
        "dbDirPath", type=str, default=".", help="""Path to database directory."""
    )
    parser = ap.add_version_option(parser)

    parser.set_defaults(parse=parse_arguments, run=run)

    return parser


@enable_rich_assert
def parse_arguments(args: argparse.Namespace) -> argparse.Namespace:
    return args


@enable_rich_assert
def run(args: argparse.Namespace) -> None:
    logging.info("Read database.")
    oligoDB = query.OligoDatabase(args.dbDirPath)
    oligoDB.read_all_chromosomes(True)
    logging.info(f'Database name: "{oligoDB.get_name()}"')

    refGenome = oligoDB.get_reference_genome()
    logging.info(f'Reference genome: "{refGenome}"')

    oligoMinDist = oligoDB.get_oligo_min_dist()
    oligoLengthRange = oligoDB.get_oligo_length_range()
    hasOverlaps = oligoDB.has_overlaps()
    logging.info(f"Contains overlaps: {hasOverlaps}")
    logging.info(f"Oligo min distance: {oligoMinDist}")
    logging.info(f"Oligo length range: {oligoLengthRange}")
    logging.info("Database checked.")

    logging.info("Done. :thumbs_up: :smiley:")
