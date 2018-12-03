# -*- coding: utf-8 -*-

'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
@description: biological file extension-specific methods.
'''



# ==============================================================================

import os
import pandas as pd

class UCSCbed(object):
    '''Class to read a UCSC Bed format file into a pandas.DataFrame.'''

    FIELD_NAMES = ["chrom", "chromStart", "chromEnd",
        "name", "score", "strand", "thickStart", "thickEnd",
        "itemRgb", "blockCount", "blockSizes", "blockStarts"]
    FIELD_FORMAT = 'siisfsiisiss'
    FORMATTER = {'f':float, 'i':int, 's':str}

    def __init__(self, path):
        super(UCSCbed, self).__init__()
        self.path = path
        self.__read()

    def __read(self):
        '''Reads the bed file into a pandas.DataFrame.'''

        assert os.path.isfile(self.path), f"bed file not found: '{self.path}'"

        bedDF = []
        with open(self.path, 'r+') as IH:
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
    
    @staticmethod
    def parse_bed_line(line):
        '''Parses and checks one line of a bed file.
        Does not work on header lines.'''
        
        line = line.strip().split("\t")
        assert 3 <= len(line), f"at least 3 fields required, {len(line)} found."

        lineDF = pd.DataFrame([
            UCSCbed.FORMATTER[UCSCbed.FIELD_FORMAT[i]](line[i])
            for i in range(len(line))]).transpose()
        lineDF.columns = UCSCbed.FIELD_NAMES[:len(line)]

        return(lineDF)

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


# END ==========================================================================

################################################################################
