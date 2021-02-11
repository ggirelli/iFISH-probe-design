"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
import configparser
from ifpd import bioext
from ifpd.scripts import arguments as ap  # type: ignore
from ifpd.exception import enable_rich_assert
import logging
import numpy as np  # type: ignore
import os
import pandas as pd  # type: ignore
from rich.logging import RichHandler  # type: ignore
import shutil

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)


def init_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        __name__.split(".")[-1],
        description="""
Builds a database of complementary oligodeoxyribonucleotides (ODNs) in a format
compatible with ifpd.

DISCLAIMER: this script does NOT generate a new database. It only re-formats an
existing database to a format compatible with ifpd.

The script takes a tabulation-separated values (tsv) file with four (4) columns:
chromosome (or feature), chromStart, chromEnd, sequence. The first three (3) column are
identical to the columns of a BED3 file.

NOTE: only non-arbitrary nucleotides in standard IUPAC format are allowed in the
ODNs sequence. https://www.bioinformatics.org/sms/iupac.html

After the database is created, we advise running the ifpd dbchk script to
test its integrity.

Details on the BED3 format are available on the UCSC website:
https://genome.ucsc.edu/FAQ/FAQformat.html#format1
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Builds a database of complementary ODNs compatible with FISH-ProDe.",
    )

    parser.add_argument(
        "input",
        metavar="input",
        type=str,
        help="""Path to input file. Four (4) tabulation-separated columns are expected:
        chromosome, chromStart, chromEnd, and sequence.""",
    )
    parser.add_argument("dbName", metavar="dbName", type=str, help="Database name.")

    parser.add_argument(
        "--output",
        metavar="dirPath",
        type=str,
        default=".",
        help="""Path to directory where to build the database. Created if missing.
            Defaults a subfolder of current directory with database name.""",
    )
    parser.add_argument(
        "--refGenome",
        metavar="refGen",
        type=str,
        default="",
        help="Reference genome. Only stored in the config file.",
    )
    parser = ap.add_version_option(parser)

    advanced = parser.add_argument_group("advanced arguments")
    advanced.add_argument(
        "--increment-chrom-end",
        action="store_const",
        dest="incrementChromEnd",
        const=True,
        default=False,
        help="""Use this option if your input bed file is not in UCSC bed format,
            and the last position (chromEnd) is actually included. This forces
            a unit increase of that position to convert to UCSC bed format.""",
    )
    advanced.add_argument(
        "--custom-config",
        metavar="config",
        type=str,
        nargs="*",
        help="""Space separated "key:value" pairs to store in the
        database .config file. No quotes needed.""",
    )
    advanced.add_argument(
        "-f",
        action="store_const",
        dest="forceRun",
        const=True,
        default=False,
        help="""Force overwriting of the database if already run.
            !!!This is potentially dangerous!!!""",
    )

    parser.set_defaults(parse=parse_arguments, run=run)

    return parser


@enable_rich_assert
def parse_arguments(args: argparse.Namespace) -> argparse.Namespace:
    if "." == args.output:
        args.output = args.dbName

    assert os.path.isfile(args.input), f'input file not found: "{args.input}"'
    assert not os.path.isfile(
        args.output
    ), f'expected output path to a folder, file found: "{args.output}"'

    if args.forceRun:
        if os.path.isdir(args.output):
            logging.warning("'-f' option used. Removing previously generated database.")
            shutil.rmtree(args.output)
            pass
    else:
        assert not os.path.isdir(
            args.output
        ), f'output folder already exists: "{args.output}"'
    return args


def sort_oligos(args, chromList):
    logging.info("Sort oligos.")
    has_overlaps = False
    oligoLengthRange = [np.inf, -np.inf]
    oligoMinDist = np.inf
    for chrom in chromList:
        chromDF = pd.read_csv(os.path.join(args.output, chrom), "\t", header=None)
        chromDF.columns = bioext.UCSCbed.FIELD_NAMES[1 : (chromDF.shape[1] + 1)]

        chromDF = chromDF.sort_values("chromStart")
        chromDF.to_csv(
            os.path.join(args.output, chrom), "\t", header=False, index=False
        )

        startPositions = np.array(chromDF["chromStart"].iloc[1:].tolist())
        endPositions = np.array(chromDF["chromEnd"].iloc[:-1].tolist()) - 1
        if any(startPositions <= endPositions):
            has_overlaps = True

        assert len(startPositions) == len(endPositions)
        if 0 == len(startPositions):
            continue
        oligoMinDist = min(oligoMinDist, min(startPositions - endPositions - 1))

        oligoLengthList = np.unique(chromDF["chromEnd"] - chromDF["chromStart"])
        oligoLengthRange[0] = min(oligoLengthRange[0], oligoLengthList.min())
        oligoLengthRange[1] = max(oligoLengthRange[1], oligoLengthList.max())
    return oligoMinDist, oligoLengthRange, has_overlaps


def mk_config(args, oligoMinDist, oligoLengthRange, has_overlaps):
    logging.info("Write config file.")
    config = configparser.ConfigParser()
    config["DATABASE"] = {"name": args.dbName, "refGenome": args.refGenome}
    config["OLIGOS"] = {
        "min_dist": oligoMinDist,
        "min_length": oligoLengthRange[0],
        "max_length": oligoLengthRange[1],
        "overlaps": str(has_overlaps),
    }
    config["SOURCE"] = {
        "bed": args.input,
        "outDirectory": args.output,
    }
    if args.custom_config is not None:
        config["CUSTOM"] = {}
        for x in args.custom_config:
            k, v = x.split(":")[:2]
            config["CUSTOM"][k] = v

    with open(os.path.join(args.output, ".config"), "w+") as OH:
        config.write(OH)


@enable_rich_assert
def run(args: argparse.Namespace) -> None:
    os.mkdir(args.output)

    logging.info("Set up input buffer.")
    oligoGenerator = bioext.UCSCbed(
        args.input, incrementChromEnd=args.incrementChromEnd, bufferize=True
    ).buffer(False, False)

    logging.info("Parse and write database.")
    chromList = set()
    for line in oligoGenerator:
        line = line.strip().split("\t")
        chrom = line.pop(0)
        line = "\t".join(line) + "\n"
        chromList.add(chrom)
        with open(os.path.join(args.output, chrom), "a+") as OH:
            OH.write(line)

    mk_config(args, *sort_oligos(args, chromList))
    logging.info(f'Created database "{args.dbName}".')

    logging.info("Done. :thumbs_up: :smiley:")
