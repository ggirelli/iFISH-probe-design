"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

# import ifpd as fp
import os
import pandas as pd  # type: ignore
from rich.progress import track  # type: ignore


class UCSCbed(object):
    """Class to read a UCSC Bed format file into a pandas.DataFrame."""

    FIELD_NAMES = [
        "chrom",
        "chromStart",
        "chromEnd",
        "name",
        "score",
        "strand",
        "thickStart",
        "thickEnd",
        "itemRgb",
        "blockCount",
        "blockSizes",
        "blockStarts",
    ]
    FIELD_FORMAT = "siisfsiisiss"
    FORMATTER = {"f": float, "i": int, "s": str}

    def __init__(self, path, incrementChromEnd=False, bufferize=False):
        super(UCSCbed, self).__init__()
        self.path = path
        self.incrementChromEnd = incrementChromEnd
        self.nrecords = self.count_records()
        if not bufferize:
            self.__read()

    def count_records(self):
        return sum(1 for line in open(self.path))

    def __read(self):
        """Reads the bed file into a pandas.DataFrame."""
        assert os.path.isfile(self.path), f"bed file not found: '{self.path}'"

        bedDF = []
        with open(self.path, "r+") as IH:
            header = next(IH)
            if header.startswith("browser") or header.startswith("track"):
                self.custom = True
                self.header = header.strip()
            else:
                bedDF.append(UCSCbed.parse_bed_line(header))
                self.custom = False
                self.header = None
            bedDF.extend([UCSCbed.parse_bed_line(line) for line in IH])

        self.df = pd.concat(bedDF)
        self.df.index = range(self.df.shape[0])
        self.ncols = self.df.shape[1]

    def __set_custom_header(self):
        with open(self.path, "r+") as IH:
            line = next(IH)
            if line.startswith("browser") or line.startswith("track"):
                self.custom = True
                self.header = line.strip()
            else:
                self.custom = False
                self.header = None

    def buffer(self, parse=True, enforceBED3=False):
        """Reads the bed file and yields one line at a time. The content is not
        stored in the class. Each call to the buffer function moves forward to
        the next line. To restart, re-initialize the class with bufferize=True.
        Use enforceBED3 to strip any additional column. Use parse to get a
        formatted pd.DataFrame instead of a raw string."""
        self.__set_custom_header()
        with open(self.path, "r+") as IH:
            if self.custom:
                next(IH)
            for line in track(IH, total=self.nrecords - 1, description="Parsing"):
                if parse:
                    yield UCSCbed.parse_bed_line(
                        line, enforceBED3, self.incrementChromEnd
                    )
                else:
                    if self.incrementChromEnd:
                        line = line.strip().split("\t")
                        line[2] = str(int(line[2]) + 1)
                        line = "\t".join(line) + "\n"
                    yield line

    @staticmethod
    def parse_bed_line(line, enforceBED3=False, incrementChromEnd=False):
        """Parses and checks one line of a bed file.
        Does not work on header lines."""

        line = line.strip().split("\t")
        assert 3 <= len(line), f"at least 3 fields required, {len(line)} found."
        line = line[: min(4 - enforceBED3, len(line))]

        lineDF = pd.DataFrame(
            [
                UCSCbed.FORMATTER[UCSCbed.FIELD_FORMAT[i]](line[i])
                for i in range(len(line))
            ]
        ).transpose()
        lineDF.columns = UCSCbed.FIELD_NAMES[: len(line)]

        lineDF.iloc[0, 2] += incrementChromEnd

        return lineDF

    def isBEDN(self, n):
        n = min(n, 12)
        return self.ncols == n

    def getBEDN(self, n):
        n = min(n, 12)
        assert self.ncols >= n
        return self.df.iloc[:, :n]

    def mkBEDN(self, n):
        assert n <= 12
        if n < self.ncols:
            self.df = self.df.iloc[:, :n]
            self.ncols = n
