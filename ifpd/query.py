"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import matplotlib  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import matplotlib.patches as patches  # type: ignore
import configparser
from ifpd import bioext, stats
from joblib import Parallel, delayed  # type: ignore
import numpy as np  # type: ignore
import os
import pandas as pd  # type: ignore
from rich.progress import track  # type: ignore
from typing import List

matplotlib.use("svg")


class OligoDatabase(object):
    """FISH-ProDe Oligonucleotide Database class."""

    def __init__(self, dbDirPath):
        super(OligoDatabase, self).__init__()
        self.dirPath = dbDirPath
        self.chromData = {}

        assert not os.path.isfile(
            self.dirPath
        ), f'expected folder, file found: "{self.dirPath}"'
        assert os.path.isdir(
            self.dirPath
        ), f'database folder not found: "{self.dirPath}"'

        configPath = os.path.join(self.dirPath, ".config")
        assert os.path.isfile(configPath), f'missing "{configPath}" file.'

        with open(configPath, "r") as IH:
            self.config = configparser.ConfigParser()
            self.config.read_string("".join(IH.readlines()))

    def check_overlaps(self):
        hasOverlaps = False
        for chrom, chromData in self.chromData.items():
            startPositions = np.array(chromData.iloc[:-1, 0])
            endPositions = np.array(chromData.iloc[1:, 1]) - 1
            foundOverlaps = any(startPositions <= endPositions)
            hasOverlaps |= foundOverlaps
        return hasOverlaps == self.has_overlaps()

    def get_oligo_length_range(self):
        """Reads oligo length range from Database .config"""
        return (
            self.config.getint("OLIGOS", "min_length"),
            self.config.getint("OLIGOS", "max_length"),
        )

    def get_oligo_min_dist(self):
        """Reads consecutive oligo minimum distance from Database .config"""
        return self.config.getint("OLIGOS", "min_dist")

    def get_name(self):
        """Reads Database name from Database .config"""
        return self.config["DATABASE"]["name"]

    def get_reference_genome(self):
        """Reads reference genome from Database .config"""
        return self.config["DATABASE"]["refGenome"]

    def has_overlaps(self):
        """Reads overlaps status from Database .config"""
        return self.config.getboolean("OLIGOS", "overlaps")

    def has_sequences(self):
        """Reads sequence status from Database .config"""
        return True

    def has_chromosome(self, chrom):
        return chrom in os.listdir(self.dirPath)

    def read_chromosome(self, chrom):
        assert self.has_chromosome(chrom)

        chromPath = os.path.join(self.dirPath, chrom)
        chromData = pd.read_csv(chromPath, "\t", header=None)
        chromData.columns = bioext.UCSCbed.FIELD_NAMES[1 : (chromData.shape[1] + 1)]

        assert 0 != chromData.shape[0], f'found empty chromosome file: "{chromPath}"'
        assert 2 <= chromData.shape[1], f'missing columns in "{chromPath}"'
        assert all(
            chromData.iloc[:, 0].diff()[1:] > 0
        ), f'found unsorted file: "{chromPath}"'
        assert all(
            chromData.iloc[:, 1].diff()[1:] >= 0
        ), 'found unsorted file: "{chromPath}"'

        oligoMinDist = self.get_oligo_min_dist()
        startValues = chromData.iloc[1:, 0].values
        endValues = chromData.iloc[:-1, 1].values
        if 0 != len(startValues):
            oligoMinD_observed = min(startValues - endValues)
        else:
            oligoMinD_observed = np.inf
        assert oligoMinD_observed >= oligoMinDist, "".join(
            [
                "oligo min distance does not match: ",
                f"{oligoMinD_observed} instead of {oligoMinDist}.",
            ]
        )

        oligoLengthRange = self.get_oligo_length_range()
        oligoLengthList = chromData.iloc[:, 1] - chromData.iloc[:, 0]
        assert all(
            oligoLengthList >= oligoLengthRange[0]
        ), f'oligo too small for ".config" in "{chromPath}"'
        assert all(
            oligoLengthList <= oligoLengthRange[1]
        ), f'oligo too big for ".config" in "{chromPath}"'

        if self.has_overlaps():
            assert self.check_overlaps(), f'overlaps status mismatch in "{chromPath}"'

        if self.has_sequences():
            assert chromData.shape[1] >= 3, f'missing sequence columns in "{chromPath}"'

        self.chromData[chrom] = chromData

    def read_all_chromosomes(self, verbose):
        chromList = [d for d in os.listdir(self.dirPath) if not d.startswith(".")]
        assert 0 < len(chromList), "no chromosome files found in {self.dirPath}"
        chromList = track(chromList) if verbose else chromList

        for chrom in chromList:
            self.read_chromosome(chrom)


class OligoProbe(object):
    """Class for probe management."""

    def __init__(self, chrom, oligos, database):
        super(OligoProbe, self).__init__()
        self.chrom = chrom
        self.oligoData = oligos
        self.refGenome = database.get_reference_genome()
        self.chromStart = self.oligoData.iloc[:, 0].min()
        self.chromEnd = self.oligoData.iloc[:, 1].max()
        self.midpoint = (self.chromStart + self.chromEnd) / 2
        self.size = self.chromEnd - self.chromStart
        self.homogeneity = self.get_probe_homogeneity()

    def __str__(self):
        s = f"[{self.refGenome}]"
        s += f"{self.chrom}:{self.chromStart}-{self.chromEnd};"
        s += f" oligoSpread: {self.homogeneity}"
        return s

    def asDataFrame(self, region=None):
        if type(None) == type(region):
            return pd.DataFrame.from_dict(
                {
                    "chrom": [self.chrom],
                    "chromStart": [self.chromStart],
                    "chromEnd": [self.chromEnd],
                    "refGenome": [self.refGenome],
                    "midpoint": [self.midpoint],
                    "size": [self.size],
                    "homogeneity": [self.homogeneity],
                }
            )
        else:
            return pd.DataFrame.from_dict(
                {
                    "chrom": [self.chrom],
                    "chromStart": [self.chromStart],
                    "chromEnd": [self.chromEnd],
                    "refGenome": [self.refGenome],
                    "midpoint": [self.midpoint],
                    "size": [self.size],
                    "homogeneity": [self.homogeneity],
                    "regChromStart": region[0],
                    "regChromEnd": region[1],
                }
            )

    def get_probe_centrality(self, region):
        """Calculate centrality, as location of the probe midpoint relative to
        the region midpoint. 1 when overlapping, 0 when the probe midpoint is
        at either of the region extremities."""
        region_halfWidth = (region[2] - region[1]) / 2
        region_midPoint = region[1] + region_halfWidth
        centrality = (
            region_halfWidth - abs(region_midPoint - self.midpoint)
        ) / region_halfWidth
        return centrality

    def get_probe_size(self):
        """Probe size, defined as difference between start of first oligo
        and end of the last one."""
        return self.oligoData.iloc[:, 1].max() - self.oligoData.iloc[:, 0].min()

    def get_probe_homogeneity(self):
        """Probe homogeneity, as the inverse of the standard deviation of the
        distance between consecutive oligos, calculated from their start
        position, disregarding oligo length."""
        std = np.std(np.diff(self.oligoData.iloc[:, 1]))
        return np.inf if 0 == std else 1 / std

    def describe(self, region, path=None):
        """Builds a small pd.DataFrame describing a probe."""
        description = pd.DataFrame.from_dict(
            {
                "chrom": [region[0]],
                "chromStart": [self.oligoData.iloc[:, 0].min()],
                "chromEnd": [self.oligoData.iloc[:, 1].max()],
                "centrality": [self.get_probe_centrality(region)],
                "size": [self.size],
                "homogeneity": [self.homogeneity],
            }
        )

        if not type(None) == type(path):
            config = configparser.ConfigParser()
            config["REGION"] = {
                "chrom": region[0],
                "chromStart": region[1],
                "chromEnd": region[2],
            }
            config["PROBE"] = {
                "chrom": description["chrom"].values[0],
                "chromStart": description["chromStart"].values[0],
                "chromEnd": description["chromEnd"].values[0],
                "nOligo": self.oligoData.shape[0],
            }
            config["FEATURES"] = {
                "centrality": description["centrality"].values[0],
                "size": description["size"].values[0],
                "homogeneity": description["homogeneity"].values[0],
            }
            with open(path, "w+") as OH:
                config.write(OH)

        return description

    def get_fasta(self, path=None, prefix=""):
        if not prefix.startswith(" "):
            prefix = " " + prefix

        fasta = ""
        for i in self.oligoData.index:
            oligo = self.oligoData.loc[i, :]
            chromStart, chromEnd, sequence = oligo[:3]
            fasta += f">{prefix}oligo_{i} [{self.refGenome}]"
            fasta += f"{self.chrom}:{chromStart}-{chromEnd}\n"
            fasta += f"{sequence}\n"

        if not type(None) == type(path):
            assert os.path.isdir(os.path.dirname(path))
            with open(path, "w+") as OH:
                OH.write(fasta)

        return fasta

    def get_bed(self, path=None, prefix=""):
        if not prefix.endswith("_"):
            prefix += "_"

        bed = f'track description="ref:{self.refGenome}"\n'
        for i in self.oligoData.index:
            oligo = self.oligoData.loc[i, :]
            chromStart, chromEnd, sequence = oligo[:3]
            bed += f"{self.chrom}\t{chromStart}\t{chromEnd}\t"
            bed += f"{prefix}oligo_{i}\n"

        if not type(None) == type(path):
            assert os.path.isdir(os.path.dirname(path))
            with open(path, "w+") as OH:
                OH.write(bed)

        return bed

    def _plot_region(self, outputDir, region):
        fig = plt.figure()

        chrom, start, stop = region
        plt.plot([start, stop], [0, 0], "k", linewidth=4.0, label="Genome")
        plt.plot(
            [start + (stop - start) / 2.0, start + (stop - start) / 2.0],
            [-1, 1],
            "r--",
            label="Window center",
        )

        plt.plot(
            [self.chromStart, self.chromEnd], [0, 0], "c-", linewidth=4.0, label="Probe"
        )
        plt.plot(
            [self.chromStart + self.size / 2.0, self.chromStart + self.size / 2.0],
            [-1, 1],
            "c--",
            label="Probe center",
        )

        plt.gca().axes.get_yaxis().set_visible(False)
        plt.suptitle("%s:%d-%.0f" % (chrom, start, stop))
        plt.xlabel("genomic coordinate [nt]")
        plt.legend(fontsize="small", loc="best")

        plt.savefig(
            os.path.join(outputDir, "window.png"), format="png", bbox_inches="tight"
        )
        plt.close(fig)

    def _plot_oligo(self, outputDir):
        fig = plt.figure(figsize=(20, 5))
        (genome_handle,) = plt.plot(
            [self.chromStart, self.chromEnd], [0, 0], "k", linewidth=4.0, label="Genome"
        )

        for i in self.oligoData.index:
            oligo = self.oligoData.loc[i, :]
            oligo_midpoint = (oligo["chromStart"] + oligo["chromEnd"]) / 2.0
            (oligo_handle,) = plt.plot(
                [oligo["chromStart"], oligo["chromEnd"]],
                [0, 0],
                "c",
                linewidth=2.0,
                label="Oligo",
            )
            (oligoCenter_handle,) = plt.plot(
                [oligo_midpoint, oligo_midpoint],
                [-0.1, 0.1],
                "c:",
                label="Oligo center",
            )

        plt.gca().axes.get_yaxis().set_visible(False)
        plt.ylim((-0.5, 0.5))

        plt.gca().axes.get_xaxis().set_ticks(
            list(
                range(
                    self.chromStart,
                    self.chromEnd,
                    max(1, int((self.chromEnd - self.chromStart) / 5.0)),
                )
            )
        )

        plt.legend(
            handles=[genome_handle, oligo_handle, oligoCenter_handle],
            fontsize="small",
            loc="best",
        )
        plt.suptitle((f"{self.chrom}:{self.chromStart}-{self.chromEnd}"))
        plt.xlabel("genomic coordinate [nt]")

        plt.savefig(
            os.path.join(outputDir, "probe.png"), format="png", bbox_inches="tight"
        )
        plt.close(fig)

    def _plot_oligo_distr(self, outputDir):
        fig = plt.figure()

        plt.plot(
            [0, self.oligoData.shape[0] - 1],
            [self.chromStart, self.chromEnd],
            "k-",
            label="Homogeneous distribution",
        )
        plt.plot(
            list(range(self.oligoData.shape[0])),
            self.oligoData["chromStart"].values,
            "r.",
            label="Oligo",
        )

        plt.suptitle(f"{self.chrom}:{self.chromStart}-{self.chromEnd}")
        plt.xlabel("oligo number")
        plt.ylabel("genomic coordinate [nt]")
        plt.legend(fontsize="small", loc="best")

        plt.savefig(os.path.join(outputDir, "oligo.png"), format="png")
        plt.close(fig)

    def _plot_oligo_distance(self, outputDir):
        fig = plt.figure()

        if 1 < self.oligoData.shape[0]:
            startPositions = self.oligoData.iloc[1:, 0].values
            endPositions = self.oligoData.iloc[:-1, 1].values
            diffs = startPositions - endPositions
            plt.hist(diffs, density=1, facecolor="green", alpha=0.5)
            density = stats.calc_density(diffs, alpha=0.5)
            plt.plot(
                density["x"].tolist(),
                density["y"].tolist(),
                "b--",
                label="Density distribution",
            )

            plt.suptitle(f"{self.chrom}:{self.chromStart}-{self.chromEnd}")
            plt.legend(fontsize="small", loc="best")

        plt.xlabel("Distance between consecutive oligos [nt]")
        plt.ylabel("Density")

        plt.savefig(os.path.join(outputDir, "distance.png"), format="png")
        plt.close(fig)

    def plot(self, outputDir, region):
        assert os.path.isdir(outputDir), f'folder not found: "{outputDir}"'
        self._plot_region(outputDir, region)
        self._plot_oligo(outputDir)
        self._plot_oligo_distr(outputDir)
        self._plot_oligo_distance(outputDir)


def describe_candidate(candidate, queried_region):
    return candidate.describe(queried_region)


class ProbeFeatureTable(object):
    FEATURE_SORT = {
        "centrality": {"ascending": False},
        "size": {"ascending": True},
        "homogeneity": {"ascending": False},
    }

    def __init__(self, candidateList, queried_region, verbose=False, threads=1):
        super(ProbeFeatureTable, self).__init__()
        assert 0 < len(candidateList)

        self.data = []
        if 1 != threads:
            verbose = 1 if verbose else 0
            self.data = Parallel(n_jobs=threads, backend="threading", verbose=verbose)(
                delayed(describe_candidate)(candidate, queried_region)
                for candidate in candidateList
            )
        else:
            candidateList = track(candidateList) if verbose else candidateList
            for candidate in candidateList:
                self.data.append(candidate.describe(queried_region))
        self.data = pd.concat(self.data)
        self.data.index = range(self.data.shape[0])

        self.discarded = None

    def reset(self):
        self.data = pd.concat([self.discarded, self.data])
        self.discarded = None
        self.data.sort_index(inplace=True)

    def keep(self, condition, cumulative=False):
        if not cumulative:
            self.reset()
        self.discarded = pd.concat(
            [self.discarded, self.data.loc[np.logical_not(condition), :]]
        )
        self.data = self.data.loc[condition, :]

    def filter(self, feature, thr, cumulative=False):
        assert (
            feature in self.FEATURE_SORT.keys()
        ), f'fetature "{feature}" not recognized.'

        if not cumulative:
            self.reset()

        self.rank(feature)

        best_feature = self.data[feature].values[0]
        feature_delta = best_feature * thr
        feature_range = (best_feature - feature_delta, best_feature + feature_delta)

        discardCondition = [self.data[feature] < feature_range[0]]
        discardCondition.append(self.data[feature] > feature_range[1])
        discardCondition = np.logical_or(*discardCondition)
        self.discarded = pd.concat([self.discarded, self.data.loc[discardCondition, :]])
        self.data = self.data.loc[np.logical_not(discardCondition), :]

        return (feature_range, feature)

    def rank(self, feature):
        self.data = self.data.sort_values(
            feature, ascending=self.FEATURE_SORT[feature]["ascending"]
        )


class GenomicWindow(object):
    def __init__(self, chrom, start, size):
        super(GenomicWindow, self).__init__()
        self.chrom = chrom
        self.chromStart = start
        self.chromEnd = start + size
        self.midpoint = (self.chromStart + self.chromEnd) / 2
        self.size = size
        self.probe = None

    def __str__(self):
        s = f"[GenomicWindow]{self.chrom}:{self.chromStart}-{self.chromEnd}\n"
        s += f" Probe: {self.probe}"
        return s

    def asRegion(self):
        return (self.chrom, self.chromStart, self.chromEnd)

    def has_probe(self):
        return self.probe is not None

    def shift(self, n):
        return GenomicWindow(self.chrom, self.chromStart + n, self.size)

    def __repr__(self):
        return f"{self.chrom}:{self.chromStart}-{self.chromEnd}"


class GenomicWindowList(object):
    """Both a list genomic window and associated probe set."""

    data: List = []

    def __init__(self, windows=None):
        super(GenomicWindowList, self).__init__()
        if type(None) != type(windows):
            self.data = windows

    def __getitem__(self, i):
        return self.data[i]

    def __iter__(self):
        for window in self.data:
            yield window

    def __len__(self):
        return len(self.data)

    def add(self, chrom, start, size):
        self.data.append(GenomicWindow(chrom, start, size))

    def count_probes(self):
        return sum([w.has_probe() for w in self])

    def shift(self, n):
        return GenomicWindowList([window.shift(n) for window in self.data])

    def sort(self):
        midpointList = np.array([w.midpoint for w in self.data])
        self.data = [self.data[i] for i in np.argsort(midpointList)]

    def calc_probe_size_and_homogeneity(self):
        if 3 > self.count_probes():
            return np.nan

        probeData = pd.concat(
            [
                w.probe.asDataFrame((w.chromStart, w.chromEnd))
                for w in self
                if w.probe is not None
            ]
        )
        size_std = probeData["size"].values.std()
        probe_homogeneity = np.std(
            probeData["chromStart"].values[1:] - probeData["chromEnd"].values[:-1]
        )
        return 2 / (size_std + probe_homogeneity)

    def asDataFrame(self):
        starts = []
        ends = []
        sizes = []
        for window in self:
            starts.append(window.chromStart)
            ends.append(window.chromEnd)
            sizes.append(window.size)
        return pd.DataFrame.from_dict(
            {"chromStart": starts, "chromEnd": ends, "size": sizes}
        )

    def _plot_probe_set(self, outputDir, region):
        fig = plt.figure(figsize=(20, 5))

        for wi in range(len(self)):
            window = self[wi]
            plt.axvline(window.chromStart, ymin=-1, ymax=1, color="k")
            if not window.has_probe():
                plt.gca().add_patch(
                    patches.Rectangle(
                        (window.chromStart, -1), window.size, 2, color="r"
                    )
                )
            plt.gca().text(window.midpoint, 0.5, wi + 1)
        plt.axvline(self[0].chromStart, ymin=-1, ymax=1, color="k", linestyle=":")
        plt.axvline(self[-1].chromEnd, ymin=-1, ymax=1, color="k", linestyle=":")

        plt.gca().add_patch(
            patches.Rectangle(
                (region[1], -1), self[0].chromStart - region[1], 2, color="k"
            )
        )
        plt.gca().add_patch(
            patches.Rectangle(
                (self[-1].chromEnd, -1), region[2] - self[-1].chromEnd, 2, color="k"
            )
        )

        (genome,) = plt.plot(
            [region[1], region[2]], [0, 0], "k", linewidth=4.0, label="Genome"
        )

        for probe in [w.probe for w in self if w.probe is not None]:
            (oligo,) = plt.plot(
                [probe.chromStart, probe.chromEnd],
                [0, 0],
                "c",
                linewidth=2.0,
                label="Probe",
            )
            (oligo_center,) = plt.plot(
                [probe.midpoint, probe.midpoint],
                [-0.1, 0.1],
                "c:",
                label="Probe center",
                linewidth=2.0,
            )

        plt.gca().axes.get_yaxis().set_visible(False)
        plt.ylim((-1, 1))
        msg = "Empty windows are reported in red."
        plt.suptitle(
            "".join(
                [
                    f"Region: {region[0]}:{region[1]}-{region[2]}",
                    " & Probe set: ",
                    f"{self[0].chrom}:{self[0].chromStart}-{self[-1].chromEnd}\n",
                    msg,
                ]
            )
        )
        plt.xlabel("genomic coordinate [nt]")

        plt.savefig(
            os.path.join(outputDir, "windows.png"), format="png", bbox_inches="tight"
        )
        plt.close(fig)

    def _plot_probe_distr(self, outputDir):
        fig = plt.figure()

        probes = [w.probe for w in self if w.probe is not None]

        if 1 < len(probes):
            plt.plot(
                [0, len(probes) - 1],
                [probes[0].midpoint, probes[-1].midpoint],
                "k-",
                label="Homogeneous distribution",
            )
            plt.plot(
                list(range(len(probes))),
                [p.midpoint for p in probes],
                "r.",
                label="Probe",
            )

            plt.suptitle(
                f"{probes[0].chrom}:" + f"{probes[0].chromStart}{probes[-1].chromEnd}"
            )
            plt.xlim((-1, len(probes)))
            plt.legend(fontsize="small", loc="best")

        plt.xlabel("probe number")
        plt.ylabel("genomic coordinate [nt]")

        plt.savefig(
            os.path.join(outputDir, "distr.png"), format="png", bbox_inches="tight"
        )
        plt.close(fig)

    def _plot_probe_distance(self, outputDir, region):
        fig = plt.figure()

        probes = [w.probe for w in self if w.probe is not None]

        if 1 < len(probes):
            starts = np.array([p.chromStart for p in probes][1:])
            ends = np.array([p.chromEnd for p in probes][:-1])
            diffs = starts - ends
            plt.hist(diffs, density=1, facecolor="green", alpha=0.5)

            density = stats.calc_density(diffs, alpha=0.5)
            plt.plot(
                density["x"].tolist(),
                density["y"].tolist(),
                "b--",
                label="Density distribution",
            )

            plt.suptitle(
                f"{probes[0].chrom}:" + f"{probes[0].chromStart}{probes[-1].chromEnd}"
            )
            plt.legend(fontsize="small", loc="best")

        plt.xlabel("Distance between consecutive probes [nt]")
        plt.ylabel("Density")

        plt.savefig(
            os.path.join(outputDir, "distance.png"), format="png", bbox_inches="tight"
        )
        plt.close(fig)

    def export(self, path, region):
        probe_counter = 0
        fasta = ""
        bed = ""
        for window in self:
            if window.has_probe():
                probe_dirName = f"probe_{probe_counter}"
                probe_dirPath = os.path.join(path, probe_dirName)
                probe = window.probe

                assert not os.path.isfile(probe_dirPath)
                assert not os.path.isdir(probe_dirPath)
                os.mkdir(probe_dirPath)

                probe.describe(
                    window.asRegion(),
                    os.path.join(probe_dirPath, f"probe_{probe_counter}.config"),
                )
                fasta += probe.get_fasta(
                    os.path.join(probe_dirPath, f"probe_{probe_counter}.fasta"),
                    f"probe{probe_counter}",
                )
                probe_bed = probe.get_bed(
                    os.path.join(probe_dirPath, f"probe_{probe_counter}.bed"),
                    f"probe{probe_counter}",
                )
                bed += "\n".join(probe_bed.split("\n")[1:])
                probe.plot(probe_dirPath, window.asRegion())

                probe_counter += 1

        self._plot_probe_set(path, region)
        self._plot_probe_distr(path)
        self._plot_probe_distance(path, region)

        return (fasta, bed)
