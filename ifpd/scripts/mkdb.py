"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
import configparser
from ifpd import bioext, web
from ifpd.scripts import arguments as ap  # type: ignore
from ifpd.exception import enable_rich_assert
import logging
import numpy as np  # type: ignore
import os
import pandas as pd  # type: ignore
from rich.logging import RichHandler  # type: ignore
import shutil
import sys

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
compatible with FISH-ProDe. This script requires a connection to internet to
contact a DAS server and obtain reference genome information. Alternatively,
if you have a local DAS server, you can specify it with the --das-uri option.
If you do not have internet connection, use the --no-net option.

DISCLAIMER: this script does NOT generate a new database. It only re-formats an
existing database to a format compatible with FISH-ProDe.

The script uses takes as input a BED file (BED3) format and the reference
genome. The reference genome name must be compatible with UCSC standard.

When building a database for FISH-ProDe, it is possible to retain the ODNs
sequence in the database itself. While this generates larger files, it also
speeds up the process of probe design, since the script would not need to
retreive the ODN sequences from somewhere else.

To retain the ODN sequences in the database, use the --retain-sequences option.
When this option is used, the ODN sequences must be present in the input BED3
file 'name' column. Alternatively, if such column is not found, the script
queries UCSC for the sequences (this process requires an active internet
connection to contact the DAS server).

NOTE: only non-arbitrary nucleotides in standard IUPAC format are allowed in the
ODNs sequence. https://www.bioinformatics.org/sms/iupac.html

After the database is created, we advise running the fprode_dbcheck script to
test its integrity.

Details on the BED3 format are available on the UCSC website:
https://genome.ucsc.edu/FAQ/FAQformat.html#format1
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Builds a database of complementary ODNs compatible with FISH-ProDe.",
    )

    parser.add_argument(
        "bedFile",
        metavar="bedPath",
        type=str,
        help="""Path to BED3 bed file. Optionally, a fourth column can be present
        with the sequence of the corresponding region""",
    )
    parser.add_argument(
        "refGenome",
        metavar="refGen",
        type=str,
        help="Reference genome in NCBI-compatible format (e.g., hg19).",
    )
    parser.add_argument("dbName", metavar="dbName", type=str, help="Database name.")

    parser.add_argument(
        "-O",
        "--output",
        metavar="dirPath",
        type=str,
        default=".",
        help="""Path to directory where to build the database. Created if missing.
            Defaults a subfolder of current directory with database name.""",
    )
    parser.add_argument(
        "--custom-config",
        metavar="config",
        type=str,
        nargs="*",
        help="""Space separated "key:value" pairs to store in the
        database .config file. No quotes needed.""",
    )

    parser.add_argument(
        "--increment-chrom-end",
        action="store_const",
        dest="incrementChromEnd",
        const=True,
        default=False,
        help="""Use this option if your input bed file is not in UCSC bed format,
            and the last position (chromEnd) is actually included. This forces
            a unit increase of that position to convert to UCSC bed format.""",
    )
    parser.add_argument(
        "--enforce-bed3",
        action="store_const",
        dest="enforceBED3",
        const=True,
        default=False,
        help="Consider only first 3 columns of the bed file.",
    )
    parser.add_argument(
        "--retain-sequences",
        action="store_const",
        dest="retainSequences",
        const=True,
        default=False,
        help="Use this option to generate a database with sequences",
    )
    parser.add_argument(
        "--list-refGenomes",
        action="store_const",
        dest="listRefGenomes",
        const=True,
        default=False,
        help="""'List UCSC reference genomes and exit
            (requires internet connection)""",
    )
    parser.add_argument(
        "-f",
        action="store_const",
        dest="forceRun",
        const=True,
        default=False,
        help="""Force overwriting of the query if already run.
            This is potentially dangerous.""",
    )
    parser.add_argument(
        "--no-net",
        action="store_const",
        dest="hasNetwork",
        const=False,
        default=True,
        help="Skip checks that require internet connection.",
    )
    parser = ap.add_version_option(parser)

    advanced = parser.add_argument_group("advanced arguments")
    advanced.add_argument(
        "--ucsc-das-uri",
        metavar="dasURI",
        type=str,
        default="http://genome.ucsc.edu/cgi-bin/das/",
        help="""URI to UCSC DAS server. Default: http://genome.ucsc.edu/cgi-bin/das/""",
    )

    parser.set_defaults(parse=parse_arguments, run=run)

    return parser


def get_refGenomeList():
    refGenomeList = []
    if "--no-net" not in sys.argv and "--list-refGenomes" in sys.argv:
        das_uri = web.get_das_uri(sys.argv)
        try:
            das_uri
        except NameError:
            pass
        else:
            refGenomeList = web.list_UCSC_reference_genomes(
                UCSC_DAS_URI=das_uri, verbose=True
            )
            sys.exit()
    return refGenomeList


@enable_rich_assert
def parse_arguments(args: argparse.Namespace) -> argparse.Namespace:
    if "." == args.output:
        args.output = args.dbName

    assert os.path.isfile(args.bedFile), f'bed file not found: "{args.bedFile}"'
    assert not os.path.isfile(
        args.output
    ), f'expected folder, file found: "{args.output}"'

    refGenomeList = get_refGenomeList()
    if 0 == len(refGenomeList) and args.hasNetwork:
        refGenomeList = web.list_UCSC_reference_genomes(
            UCSC_DAS_URI=args.das_uri, verbose=False
        )
        assert_msg = f'genome "{args.refGenome}" not found @DAS'
        assert args.refGenome in refGenomeList, assert_msg

    if args.forceRun:
        if os.path.isdir(args.output):
            shutil.rmtree(args.output)
            pass
    else:
        assert_msg = f'output folder already exists: "{args.output}"'
        assert not os.path.isdir(args.output), assert_msg
    return args


def sort_oligos(args, chromList):
    logging.info("Sorting oligos...")
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

        oligoMinDist = min(oligoMinDist, min(startPositions - endPositions - 1))

        oligoLengthList = np.unique(chromDF["chromEnd"] - chromDF["chromStart"])
        oligoLengthRange[0] = min(oligoLengthRange[0], oligoLengthList.min())
        oligoLengthRange[1] = max(oligoLengthRange[1], oligoLengthList.max())
    return oligoMinDist, oligoLengthRange, has_overlaps


def mk_config(args, oligoMinDist, oligoLengthRange, has_overlaps):
    logging.info("Generating config file...")
    config = configparser.ConfigParser()
    config["DATABASE"] = {"name": args.dbName, "refGenome": args.refGenome}
    config["OLIGOS"] = {
        "sequence": args.retainSequences,
        "min_dist": oligoMinDist,
        "min_length": oligoLengthRange[0],
        "max_length": oligoLengthRange[1],
        "overlaps": str(has_overlaps),
    }
    config["SOURCE"] = {
        "bed": args.bedFile,
        "enforced2bed3": args.enforceBED3,
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

    formatString = "%(asctime)-25s %(name)s %(levelname)-8s %(message)s"
    formatter = logging.Formatter(formatString)
    logging.basicConfig(
        filename=os.path.join(args.output, ".log"),
        level=logging.DEBUG,
        format=formatString,
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)

    if args.forceRun and os.path.isdir(args.output):
        logging.warning("Overwritten previously run query.")

    logging.info("Buffering bed-like file...")
    bed = bioext.UCSCbed(
        args.bedFile, incrementChromEnd=args.incrementChromEnd, bufferize=True
    )

    oligoGenerator = bed.buffer(False, args.enforceBED3)
    if args.retainSequences:
        logging.info("Enabled sequence retrieval from UCSC...")
        raise NotImplementedError
        # oligoGenerator = bioext.UCSCbed.add_sequence_to_raw_record(
        #     oligoGenerator, args.hasNetwork
        # )

    logging.info("Writing database...")
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
