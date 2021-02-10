"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from ifpd import query
from ifpd.scripts import arguments as ap  # type: ignore
from ifpd.exception import enable_rich_assert
import logging
import numpy as np  # type: ignore
import os
import re
from rich.logging import RichHandler  # type: ignore
import shutil
from tqdm import tqdm  # type: ignore

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)

featureList = ["size", "homogeneity", "centrality"]


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
        "region",
        metavar="region",
        type=str,
        help="Region of interest in chrN:XXX,YYY format.",
    )
    parser.add_argument(
        "database", metavar="database", type=str, help="Path to database folder."
    )
    parser.add_argument(
        "outdir",
        metavar="outputDirectory",
        type=str,
        help="Path to query output directory. Stops if it exists already.",
    )

    parser.add_argument(
        "--order",
        metavar="featOrder",
        type=str,
        default=featureList,
        nargs="+",
        help="""Space-separated features, used as explained in script description.
        The available features are: centrality, size, and homogeneity. At least 2
        features must be listed. Default: "size homogeneity centrality".""",
    )
    parser.add_argument(
        "--filter-thr",
        metavar="filterThr",
        type=float,
        default=0.1,
        help="""Threshold of first feature filter, used to identify
        a range around the best value (percentage range around it). Accepts values
        from 0 to 1. Default: 0.1""",
    )
    parser.add_argument(
        "--min-d",
        metavar="minD",
        type=int,
        default=10,
        help="*DEPRECATED* Minimum distance between consecutive oligos. Default: 10",
    )
    parser.add_argument(
        "--n-oligo",
        metavar="nOligo",
        type=int,
        default=48,
        help="Number of oligos per probe. Default: 48",
    )
    parser.add_argument(
        "--max-probes",
        metavar="maxProbes",
        type=int,
        default=-1,
        help="""Maximum number of probe candidates to output.
            Set to -1 to retrieve all candidates. Default: -1""",
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
    parser = ap.add_version_option(parser)

    parser.set_defaults(parse=parse_arguments, run=run)

    return parser


@enable_rich_assert
def parse_arguments(args: argparse.Namespace) -> argparse.Namespace:
    assert not os.path.isfile(
        args.outdir
    ), f"output folder expected, file found: {args.outdir}"
    if args.forceRun:
        if os.path.isdir(args.outdir):
            shutil.rmtree(args.outdir)
    else:
        assert not os.path.isdir(
            args.outdir
        ), f"output folder already exists: {args.outdir}"

    roi_regexp = "^chr[0-9A-Za-z]+:[0-9]+,[0-9]+$"
    assert_msg = "the provided region does not match the expected pattern:"
    assert_msg += f' "{args.region}" [chrN:XXX:YYY]'
    assert re.match(roi_regexp, args.region) is not None, assert_msg

    assert_msg = f"at least 2 features needed, only {len(args.order)} found."
    assert 2 <= len(args.order), assert_msg
    for o in args.order:
        assert_msg = f'unrecognized feature "{o}". Should be one of {featureList}.'
        assert o in featureList, assert_msg

    assert_msg = f"first filter threshold must be a fraction: {args.filter_thr}"
    assert 0 <= args.filter_thr and 1 >= args.filter_thr, assert_msg

    assert_msg = "negative minimum distance between consecutive oligos: "
    assert_msg += f"{args.min_d}"
    assert args.min_d >= 0, assert_msg

    assert args.n_oligo >= 1, f"a probe must have oligos: {args.n_oligo}"
    if args.max_probes == -1:
        args.max_probes = np.inf
    assert_msg = f"at least 1 probe in output: {args.max_probes}"
    assert args.max_probes >= 0, assert_msg

    return args


def setup_log(args):
    formatString = "%(asctime)-25s %(name)s %(levelname)-8s %(message)s"
    formatter = logging.Formatter(formatString)
    logging.basicConfig(
        filename=os.path.join(args.outdir, "log"),
        level=logging.INFO,
        format=formatString,
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)
    if args.forceRun and os.path.isdir(args.outdir):
        logging.info("Overwriting previously run query.")


@enable_rich_assert
def run(args: argparse.Namespace) -> None:
    os.mkdir(args.outdir)
    setup_log(args)

    logging.info("Reading database...")
    oligoDB = query.OligoDatabase(args.database, False)

    chrom = args.region.split(":")[0]
    chromStart, chromEnd = [int(x) for x in args.region.split(":")[1].split(",")]
    queried_region = (chrom, chromStart, chromEnd)

    assert_msg = "databases with overlapping oligos are not supported yet."
    assert not oligoDB.has_overlaps(), assert_msg

    assert_msg = f'chromosome "{chrom}" not in the database.'
    assert oligoDB.has_chromosome(chrom), assert_msg

    oligoDB.read_chromosome(chrom)
    chromData = oligoDB.chromData[chrom]

    selectCondition = np.logical_and(
        chromData.iloc[:, 0] >= chromStart, chromData.iloc[:, 1] <= chromEnd
    )
    selectedOligos = chromData.loc[selectCondition, :]

    assert_msg = "there are not enough oligos in the database."
    assert_msg += f" Asked for {args.n_oligo}, {selectCondition.sum()} found."
    assert args.n_oligo <= selectCondition.sum(), assert_msg
    logging.info(f"Found {selectCondition.sum()} oligos in {args.region}")

    if 3 > selectedOligos.shape[1]:
        logging.info("Retrieving sequences from UCSC...")
        raise NotImplementedError
        # sequences = []
        # for i in tqdm(selectedOligos.index):
        #     region = selectedOligos.iloc[i, :2].tolist()
        #     regionSequence = fp.web.get_sequence_from_UCSC(
        #         config["DATABASE"]["refGenome"], chrom, *region
        #     )
        #     sequences.append(regionSequence)
        # selectedOligos.assign(name=pd.Series(sequences,
        #                       index=selectedOligos.index).values)

    logging.info("Building probe candidates...")
    candidateList = []
    for i in tqdm(range(0, selectedOligos.shape[0] - args.n_oligo)):
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
