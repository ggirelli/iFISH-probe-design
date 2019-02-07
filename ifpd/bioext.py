# -*- coding: utf-8 -*-

'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
@description: biological file extension-specific methods.
'''



# ==============================================================================

import ifpd as fp
import io
import os
import pandas as pd
from tqdm import tqdm

class UCSCbed(object):
    '''Class to read a UCSC Bed format file into a pandas.DataFrame.'''

    FIELD_NAMES = ["chrom", "chromStart", "chromEnd",
        "name", "score", "strand", "thickStart", "thickEnd",
        "itemRgb", "blockCount", "blockSizes", "blockStarts"]
    FIELD_FORMAT = 'siisfsiisiss'
    FORMATTER = {'f':float, 'i':int, 's':str}

    def __init__(self, path, incrementChromEnd = False, bufferize = False):
        super(UCSCbed, self).__init__()
        self.path = path
        self.incrementChromEnd = incrementChromEnd
        self.nrecords = self.count_records()
        if not bufferize:
            self.__read()
    
    def count_records(self):
        return sum(1 for line in open(self.path))

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

    def buffer(self, parse = True, enforceBED3 = False):
        '''Reads the bed file and yields one line at a time. The content is not
        stored in the class. Each call to the buffer function moves forward to
        the next line. To restart, re-initialize the class with bufferize=True.
        Use enforceBED3 to strip any additional column. Use parse to get a
        formatted pd.DataFrame instead of a raw string.'''

        with open(self.path, 'r+') as IH:
            line = next(IH)
            if line.startswith("browser") or line.startswith("track"):
                self.custom = True
                self.header = line.strip()
            else:
                self.custom = False
                self.header = None

        with open(self.path, 'r+') as IH:
            if self.custom:
                next(IH)
            for line in tqdm(IH, total = self.nrecords-1):
                if parse:
                    yield UCSCbed.parse_bed_line(line,
                        enforceBED3, self.incrementChromEnd)
                else:
                    if self.incrementChromEnd:
                        line = line.strip().split("\t")
                        line[2] = str(int(line[2]) + 1)
                        line = "\t".join(line) + '\n'
                    yield line

    @staticmethod
    def parse_bed_line(line, enforceBED3 = False, incrementChromEnd = False):
        '''Parses and checks one line of a bed file.
        Does not work on header lines.'''
        
        line = line.strip().split("\t")
        assert 3 <= len(line), f"at least 3 fields required, {len(line)} found."
        line = line[:min(4 - enforceBED3, len(line))]

        lineDF = pd.DataFrame([
            UCSCbed.FORMATTER[UCSCbed.FIELD_FORMAT[i]](line[i])
            for i in range(len(line))]).transpose()
        lineDF.columns = UCSCbed.FIELD_NAMES[:len(line)]

        lineDF.iloc[0, 2] += incrementChromEnd

        return(lineDF)

    @staticmethod
    def add_sequence_to_raw_record(bedRecords, hasNetwork = False):
        for record in bedRecords:
            assert type("") == type(record)
            record = record.strip().split("\t")

            assert_msg = "each record must have at least 3 columns,"
            assert_msg += f" {len(record)} found."
            assert 3 <= len(record), assert_msg

            if 4 > len(record) and hasNetwork:
                oligoSequence = fp.web.get_sequence_from_UCSC(
                    (record[0], int(record[1]), int(record[2])), args.refGenome)
                record.append(oligoSequence)
            record = record[:4]
            yield("\t".join(record) + '\n')

    @staticmethod
    def add_sequence_to_parsed_record(bedRecords):
        for record in bedRecords:
            assert type(pd.DataFrame()) == type(bedRecords)

            assert_msg = "each record must have at least 3 columns,"
            assert_msg += f" {record.shape[0]} found."
            assert 3 <= record.shape[0]
            
            if 4 > record.shape[1]:
                region = record.loc[:, ['chrom', 'chromStart', 'chromEnd']
                    ].iloc[0, :].tolist()
                oligoSequence = fp.web.get_sequence_from_UCSC(
                    tuple(region), args.refGenome)
                record.append(oligoSequence)
            record = record.iloc[0, :4]
            yield(record)

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
