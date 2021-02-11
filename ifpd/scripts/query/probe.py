"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from ifpd import const, query
from ifpd.scripts import arguments as ap  # type: ignore
from ifpd.exception import enable_rich_assert
import logging
import numpy as np  # type: ignore
import os
from rich.logging import RichHandler  # type: ignore
from rich.progress import track  # type: ignore
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
Design a FISH probe in a genomic region of interest using a database of
oligonucleotides. Concisely, the script does the following:
- Identify all probe candidates
- Calculate centrality, size, and homogeneity for each candidate
- Identify the candidate with the best first feature (featOrder), i.e.,
  max(centrality), min(size), or max(homogeneity).
- Build a range around the best first feature value (filterThr) and filter out
  all the candidates that do not fall in it.
- Rank the remaining candidates based on the second feature (featOrder), i.e.,
  decreasing for centrality, increasing for size or homogeneity.
- Return the top N candidates (maxProbes), with plots, tables, fasta and bed.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Design a FISH probe in a genomic region of interest.",
    )

    parser.add_argument(
        "database", metavar="database", type=str, help="Path to database folder."
    )
    parser.add_argument(
        "chrom",
        type=str,
        help="Database feature to query for a probe.",
    )
    parser.add_argument(
        "outdir",
        metavar="outDir",
        type=str,
        help="Path to query output directory. Stops if it exists already.",
    )

    parser.add_argument(
        "--region",
        metavar=("chromStart", "chromEnd"),
        type=int,
        nargs=2,
        default=(0, np.inf),
        help="""Start and end locations (space-separated) of the region of interest.
        When a region is not provided (or start/end coincide),
        the whole feature is queried.""",
    )
    parser.add_argument(
        "--n-oligo",
        metavar="nOligo",
        type=int,
        default=48,
        help="""Number of oligos per probe. If not enough oligos are found, the largest
        probe (with greater number of oligos) is designed by default. Default: 48""",
    )
    parser.add_argument(
        "--max-probes",
        metavar="nProbes",
        type=int,
        default=-1,
        help="""Maximum number of probe candidates to output.
            Set to -1 to retrieve all candidates. Default: -1""",
    )

    parser = ap.add_version_option(parser)

    advanced = parser.add_argument_group("advanced arguments")
    advanced.add_argument(
        "--order",
        metavar="feature",
        type=str,
        default=const.featureList,
        nargs="+",
        help="""Space-separated features, used as explained in script description.
        The available features are: 'centrality', 'size', and 'homogeneity'. At least 2
        features must be listed. Default: "size homogeneity centrality".""",
    )
    advanced.add_argument(
        "--filter-thr",
        metavar="filterThr",
        type=float,
        default=0.1,
        help="""Threshold of first feature filter, used to identify
        a range around the best value (percentage range around it). Accepts values
        from 0 to 1. Default: 0.1""",
    )
    advanced.add_argument(
        "--min-d",
        metavar="minD",
        type=int,
        default=10,
        help="*DEPRECATED* Minimum distance between consecutive oligos. Default: 10",
    )
    advanced.add_argument(
        "--exact-n-oligo",
        action="store_const",
        dest="exact_n_oligo",
        const=True,
        default=False,
        help="""Stop if not enough oligos are found,
        instead of designing the largest probe.""",
    )
    advanced.add_argument(
        "-f",
        action="store_const",
        dest="forceRun",
        const=True,
        default=False,
        help="""Force overwriting of the query if already run.
            !!!This is potentially dangerous!!!""",
    )

    parser.set_defaults(parse=parse_arguments, run=run)

    return parser


def assert_region(args):
    if args.region is not None:
        if args.region[0] == args.region[1]:
            args.region = None
            return
        assert (
            args.region[0] >= 0
        ), f"start location cannot be negative [{args.region[0]}]."
        assert (
            args.region[1] >= 0
        ), f"end location cannot be negative [{args.region[1]}]."
        assert (
            args.region[1] > args.region[0]
        ), f"end location must be greater than start location [{args.region}]."


@enable_rich_assert
def parse_arguments(args: argparse.Namespace) -> argparse.Namespace:
    assert not os.path.isfile(
        args.outdir
    ), f"output folder expected, file found: {args.outdir}"
    if args.forceRun:
        if os.path.isdir(args.outdir):
            shutil.rmtree(args.outdir)
            logging.warning("Overwriting previously run query.")
    else:
        assert not os.path.isdir(
            args.outdir
        ), f"output folder already exists: {args.outdir}"
    assert_region(args)

    assert 2 <= len(
        args.order
    ), f"at least 2 features needed, only {len(args.order)} found."

    for o in args.order:
        assert (
            o in const.featureList
        ), f'unrecognized feature "{o}". Should be one of {const.featureList}.'

    assert (
        0 <= args.filter_thr and 1 >= args.filter_thr
    ), "first filter threshold must be a fraction: {args.filter_thr}"

    assert (
        args.min_d >= 0
    ), f"negative minimum distance between consecutive oligos: {args.min_d}"

    assert args.n_oligo >= 1, f"a probe must have oligos: {args.n_oligo}"
    if args.max_probes == -1:
        args.max_probes = np.inf
    assert args.max_probes >= 0, f"at least 1 probe in output: {args.max_probes}"

    return args


@enable_rich_assert
def run(args: argparse.Namespace) -> None:
    os.mkdir(args.outdir)
    ap.add_log_file_handler(os.path.join(args.outdir, "log"))

    logging.info("Read database.")
    oligoDB = query.OligoDatabase(args.database)

    assert (
        not oligoDB.has_overlaps()
    ), "databases with overlapping oligos are not supported yet."
    assert oligoDB.has_chromosome(
        args.chrom
    ), f'chromosome "{args.chrom}" not in the database.'

    oligoDB.read_chromosome(args.chrom)
    chromData = oligoDB.chromData[args.chrom]
    if args.region[1] == np.inf:
        args.region = (args.region[0], chromData["chromEnd"].max())
    chromStart, chromEnd = args.region
    queried_region = (args.chrom, chromStart, chromEnd)

    selectCondition = np.logical_and(
        chromData.iloc[:, 0] >= chromStart, chromData.iloc[:, 1] <= chromEnd
    )
    selectedOligos = chromData.loc[selectCondition, :]

    args = ap.check_n_oligo(args, selectCondition)

    logging.info("Build probe candidates.")
    candidateList = []
    for i in track(
        range(0, selectedOligos.shape[0] - args.n_oligo + 1), description="Building"
    ):
        candidateList.append(
            query.OligoProbe(
                queried_region[0],
                selectedOligos.iloc[i : (i + args.n_oligo), :],
                oligoDB,
            )
        )
    logging.info(f"Found {len(candidateList)} probe candidates.")

    logging.info("Describing candidates...")
    probeFeatureTable = query.ProbeFeatureTable(candidateList, queried_region, True)
    feature_range, feature = probeFeatureTable.filter(args.order[0], args.filter_thr)
    feature_range = np.round(feature_range, 6)
    logging.info(
        "".join(
            [
                f"Selected {probeFeatureTable.data.shape[0]} candidates ",
                f"in the range {feature_range} of '{feature}'.",
            ]
        )
    )

    logging.info(f"Ranking based on '{args.order[1]}'.")
    probeFeatureTable.rank(args.order[1])

    logging.info("Writing description table...")
    probeFeatureTable.data.to_csv(
        os.path.join(args.outdir, "candidates.tsv"), "\t", index=False
    )

    if np.isfinite(args.max_probes):
        logging.info(f"Exporting top {args.max_probes} candidates...")
    else:
        logging.info("Exporting candidates...")
    for i in range(min(args.max_probes, probeFeatureTable.data.shape[0])):
        candidate = candidateList[probeFeatureTable.data.index[i]]
        candidatePath = os.path.join(args.outdir, f"candidate_{i}")
        os.mkdir(candidatePath)
        candidate.describe(
            queried_region, os.path.join(candidatePath, f"candidate_{i}.config")
        )
        candidate.get_fasta(os.path.join(candidatePath, f"candidate_{i}.fasta"))
        candidate.get_bed(os.path.join(candidatePath, f"candidate_{i}.bed"))
        candidate.plot(candidatePath, queried_region)

    logging.info("Done. :thumbs_up: :smiley:")
