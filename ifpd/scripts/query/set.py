"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from ifpd import const, query
from ifpd.scripts import arguments as ap  # type: ignore
from ifpd.exception import enable_rich_assert
from joblib import Parallel, delayed  # type: ignore
import logging
import numpy as np  # type: ignore
import os
import pandas as pd  # type: ignore
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
Design a FISH probe set in a genomic region, with the aim of having the probes
as homogeneously spaced as possible. Concisely, the script does the following:
- Identify all probe candidates
- Calculate centrality, size, and homogeneity for each candidate
- Build a set of consecutive (nProbes+1) windows of the same size
    + Shift the windows set to build additional windows sets. Each windows set
      will produce one probe set candidate.
- For each window set:
    + Find the best probe in each window.
    + Aggregate each window's best probe into a candidate probe set.
- Rank candidate probe sets based on probe homogeneity.
- Return the top N candidates (maxSets), with plots, tables, fasta and bed.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Design a FISH probe set in a genomic region.",
    )
    parser.add_argument(
        "database", metavar="database", type=str, help="Path to database folder."
    )

    parser.add_argument(
        "chrom",
        type=str,
        help="Database feature to query for a probe set.",
    )
    parser.add_argument(
        "outdir",
        metavar="outDir",
        type=str,
        help="Path to query output directory. Stops if it exists already.",
    )
    parser.add_argument(
        "nProbes", metavar="nProbes", type=int, help="Number of probes to design."
    )

    parser.add_argument(
        "--region",
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
        help="Number of oligos per probe. Default: 48",
    )
    parser.add_argument(
        "--max-sets",
        metavar="maxProbes",
        type=int,
        default=-1,
        help="""Maximum number of probe set candidates to output.
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
        default=0,
        help="*DEPRECATED* Minimum distance between consecutive oligos. Default: 1",
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
        "--window-shift",
        metavar="winShift",
        type=float,
        default=0.1,
        help="""Window fraction for windows shifting.""",
    )
    advanced.add_argument(
        "-t",
        "--threads",
        metavar="nthreads",
        type=int,
        help="""Number of threads for parallelization. Default: 1""",
        default=1,
    )
    advanced.add_argument(
        "-f",
        action="store_const",
        dest="forceRun",
        const=True,
        default=False,
        help="""Force overwriting of the query if already run.
            This is potentially dangerous.""",
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
    ), f"at least 2 features need, only {len(args.order)} found."
    for o in args.order:
        assert (
            o in const.featureList
        ), f'unrecognized feature "{o}". Should be one of {const.featureList}.'
    assert (
        0 <= args.filter_thr and 1 >= args.filter_thr
    ), f"first filter threshold must be a fraction: {args.filter_thr}"
    assert (
        0 < args.window_shift and 1 >= args.window_shift
    ), f"window shift must be a fraction: {args.window_shift}"
    assert (
        args.min_d >= 0
    ), f"negative minimum distance between consecutive oligos: {args.min_d}"
    assert args.n_oligo >= 1, f"a probe must have oligos: {args.n_oligo}"
    if args.max_sets == -1:
        args.max_sets = np.inf
    assert args.max_sets >= 0, f"at least 1 probe set in output: {args.max_sets}"

    return args


def init_db(
    args,
    oligoDB,
):
    assert (
        not oligoDB.has_overlaps()
    ), "databases with overlapping oligos are not supported yet."

    if args.chrom not in oligoDB.chromData.keys():
        oligoDB.read_chromosome(args.chrom)
    chromData = oligoDB.chromData[args.chrom]
    if args.region[1] == np.inf:
        args.region = (
            args.region[0],
            oligoDB.chromData[args.chrom]["chromEnd"].max(),
        )
    chromStart, chromEnd = args.region
    queried_region = (args.chrom, chromStart, chromEnd)

    selectCondition = np.logical_and(
        chromData.iloc[:, 0] >= chromStart, chromData.iloc[:, 1] <= chromEnd
    )
    selectedOligos = chromData.loc[selectCondition, :]

    return oligoDB, queried_region, selectCondition, selectedOligos


def build_candidates(args, queried_region, selectedOligos, oligoDB):
    logging.info("Build probe candidates.")
    args.threads = ap.check_threads(args.threads)
    if 1 != args.threads:
        candidateList = Parallel(n_jobs=args.threads, backend="threading", verbose=1)(
            delayed(query.OligoProbe)(
                queried_region[0],
                selectedOligos.iloc[ii : (ii + args.n_oligo), :],
                oligoDB,
            )
            for ii in range(0, selectedOligos.shape[0] - args.n_oligo + 1)
        )
    else:
        candidateList = []
        for i in track(range(0, selectedOligos.shape[0] - args.n_oligo + 1)):
            candidateList.append(
                query.OligoProbe(
                    queried_region[0],
                    selectedOligos.iloc[i : (i + args.n_oligo), :],
                    oligoDB,
                )
            )
    logging.info(f"Found {len(candidateList)} probe candidates.")

    return candidateList


def build_windows(args, queried_region, oligoDB):
    chrom, chromStart, chromEnd = queried_region
    logging.info("Building window sets...")
    window_set = query.GenomicWindowList(None)
    window_size = chromEnd - chromStart
    window_size /= args.nProbes + 1
    window_size = int(window_size)

    skip = 1 + (0 != (chromEnd - chromStart) % window_size)
    for startPosition in range(chromStart, chromEnd, window_size)[:-skip]:
        window_set.add(chrom, startPosition, window_size)

    window_shift = max(
        int(args.window_shift * window_size),
        args.min_d + oligoDB.get_oligo_length_range()[0],
    )

    window_setList = []
    for s in range(0, window_size, window_shift):
        window_setList.append(window_set.shift(s))
    logging.info(f" Built {len(window_setList)} window sets.")

    return window_setList


def export_window_set(args, queried_region, window_setList, wsi):
    window_set = window_setList[wsi]
    window_set_path = os.path.join(args.outdir, f"probe_set_{wsi}")
    assert not os.path.isfile(window_set_path)
    assert not os.path.isdir(window_set_path)
    os.mkdir(window_set_path)

    fasta, bed = window_set.export(window_set_path, queried_region)
    fasta_path = os.path.join(window_set_path, f"probe_set_{wsi}.fa")
    bed_path = os.path.join(window_set_path, f"probe_set_{wsi}.bed")
    with open(fasta_path, "w+") as OH:
        OH.write(fasta)
    with open(bed_path, "w+") as OH:
        OH.write(bed)


def build_feature_table(args, queried_region, candidateList):
    logging.info("Describe candidates.")
    probeFeatureTable = query.ProbeFeatureTable(
        candidateList, queried_region, True, args.threads
    )

    logging.info("Write description table.")
    probeFeatureTable.data.to_csv(
        os.path.join(args.outdir, "probe_candidates.tsv"), "\t", index=False
    )

    assert args.nProbes <= probeFeatureTable.data.shape[0], "".join(
        [
            "not enough probes in the region of interest: ",
            f"{probeFeatureTable.data.shape[0]}/{args.nProbes}",
        ]
    )

    return probeFeatureTable


def populate_windows(args, candidateList, window_setList, probeFeatureTable):
    for wsi in range(len(window_setList)):
        window_set = window_setList[wsi]
        for wi in range(len(window_set)):
            window = window_set[wi]
            probeFeatureTable.reset()

            selectCondition = np.logical_and(
                probeFeatureTable.data.loc[:, "chromStart"] >= window.chromStart,
                probeFeatureTable.data.loc[:, "chromEnd"] <= window.chromEnd,
            )
            logging.info(
                "".join(
                    [
                        f"Found {selectCondition.sum()} probe candidates",
                        f" in window #{wi} of set #{wsi}.",
                    ]
                )
            )

            if 0 == selectCondition.sum():
                window_setList[wsi][wi].probe = None
                continue
            elif 1 != selectCondition.sum():
                probeFeatureTable.keep(selectCondition, cumulative=True)
                feature_range, feature = probeFeatureTable.filter(
                    args.order[0], args.filter_thr, cumulative=True
                )
                feature_range = np.round(feature_range, 6)
                logging.info(
                    "".join(
                        [
                            f" Selected {probeFeatureTable.data.shape[0]}",
                            f" candidates in the range {feature_range} of '{feature}'.",
                        ]
                    )
                )
                logging.info(
                    " Ranking probe candidates based on" + f" '{args.order[1]}'."
                )
                probeFeatureTable.rank(args.order[1])

            window_setList[wsi][wi].probe = candidateList[
                probeFeatureTable.data.index[0]
            ]
    return window_setList


@enable_rich_assert
def run(args: argparse.Namespace) -> None:
    os.mkdir(args.outdir)
    ap.add_log_file_handler(os.path.join(args.outdir, "log"))

    logging.info("Read database.")
    oligoDB = query.OligoDatabase(args.database)
    oligoDB, queried_region, selectCondition, selectedOligos = init_db(args, oligoDB)
    args = ap.check_n_oligo(args, selectCondition)

    candidateList = build_candidates(args, queried_region, selectedOligos, oligoDB)
    probeFeatureTable = build_feature_table(args, queried_region, candidateList)
    window_setList = build_windows(args, queried_region, oligoDB)
    window_setList = populate_windows(
        args, candidateList, window_setList, probeFeatureTable
    )

    logging.info("Compare probe set candidates.")
    probeSetSpread = np.array(
        [ws.calc_probe_size_and_homogeneity() for ws in window_setList]
    )
    probeCount = np.array([ws.count_probes() for ws in window_setList])
    logging.info(
        "".join(
            [
                f" {sum(probeCount == args.nProbes)}/{len(window_setList)}",
                f" probe set candidates have {args.nProbes} probes.",
            ]
        )
    )

    logging.info("Rank based on #probes and homogeneity (of probes and size).")
    probeSetData = pd.DataFrame.from_dict(
        {
            "id": range(len(window_setList)),
            "homogeneity": probeSetSpread[np.argsort(probeCount)[::-1]],
            "nProbes": probeCount[np.argsort(probeCount)[::-1]],
        }
    )
    probeSetData.sort_values(
        by=["nProbes", "homogeneity"], ascending=[False, False], inplace=True
    )
    probeSetData.drop("id", axis=1).to_csv(
        os.path.join(args.outdir, "set_candidates.tsv"), "\t", index=False
    )

    logging.info("Export probe set candidates.")
    window_setList = [window_setList[i] for i in probeSetData["id"].values]

    if 1 != args.threads:
        Parallel(n_jobs=args.threads, verbose=1)(
            delayed(export_window_set)(args, queried_region, window_setList, wsi)
            for wsi in range(len(window_setList))
        )
    else:
        for wsi in track(range(len(window_setList))):
            export_window_set(args, queried_region, window_setList, wsi)

    logging.info("Done. :thumbs_up: :smiley:")
