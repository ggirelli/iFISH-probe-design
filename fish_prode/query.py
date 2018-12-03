# -*- coding: utf-8 -*-

'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
@description: methods related to database query.
'''

# DEPENDENCIES =================================================================

import configparser
import fish_prode as fp
import numpy as np
import os
import pandas as pd
from tqdm import tqdm

# ==============================================================================

class OligoDatabase(object):
    """FISH-ProDe Oligonucleotide Database class."""

    def __init__(self, dbDirPath, verbose = False, hasNetwork = True,
        UCSC_DAS_URI = fp.web.UCSC_DAS_URI):
        super(OligoDatabase, self).__init__()
        self.dirPath = dbDirPath
        self.hasNetwork = hasNetwork
        self.UCSC_DAS_URI = UCSC_DAS_URI

        assert_msg = f'expected folder, file found: "{self.dirPath}"'
        assert not os.path.isfile(self.dirPath), assert_msg

        assert_msg = f'database folder not found: "{self.dirPath}"'
        assert os.path.isdir(self.dirPath), assert_msg

        configPath = os.path.join(self.dirPath, ".config")
        assert_msg = f'missing "{configPath}" file.'
        assert os.path.isfile(configPath), assert_msg

        IH = open(configPath, 'r')
        self.config = configparser.ConfigParser()
        self.config.read_string("".join(IH.readlines()))
        IH.close()

        if self.hasNetwork:
            refGenome = self.get_reference_genome()
            refGenomeChecked = fp.web.check_reference_genome(
                refGenome, self.UCSC_DAS_URI)
            assert refGenomeChecked, f'genome "{refGenome}" not found @UCSC'

        self._read_chromosomes(verbose)

    def check_overlaps(self):
        hasOverlaps = False
        for chrom, chromData in self.chromData.items():
            startPositions = np.array(chromData.iloc[:-1, 0])
            endPositions = np.array(chromData.iloc[1:, 1]) - 1
            foundOverlaps = any(startPositions <= endPositions)
            hasOverlaps |= foundOverlaps
        return hasOverlaps == self.has_overlaps()

    def get_oligo_length_range(self):
        '''Reads oligo length range from Database .config'''
        return (
            self.config.getint('OLIGOS', 'min_length'),
            self.config.getint('OLIGOS', 'max_length')
        )

    def get_name(self):
        '''Reads Database name from Database .config'''
        return self.config['DATABASE']['name']

    def get_reference_genome(self):
        '''Reads reference genome from Database .config'''
        return self.config['DATABASE']['refGenome']

    def has_overlaps(self):
        '''Reads overlaps status from Database .config'''
        return self.config.getboolean('OLIGOS', 'overlaps')

    def has_sequences(self):
        '''Reads sequence status from Database .config'''
        return self.config.getboolean('OLIGOS', 'sequence')

    def _read_chromosomes(self, verbose):

        chromList = [d for d in os.listdir(self.dirPath) if d != '.config']
        assert 1 < len(chromList), "no chromosome files found in {self.dirPath}"
        chromList = tqdm(chromList) if verbose else chromList

        self.chromData = {}
        for chrom in chromList:
            chromPath = os.path.join(self.dirPath, chrom)
            chromData = pd.read_csv(chromPath, '\t', header = None)
            chromData.columns = fp.bioext.UCSCbed.FIELD_NAMES[
                1:(chromData.shape[1]+1)]

            assert_msg = f'found empty chromosome file: "{chromPath}"'
            assert 0 != chromData.shape[0], assert_msg

            assert_msg = f'missing columns in "{chromPath}"'
            assert 2 <= chromData.shape[1], assert_msg

            assert_msg = f'found unsorted file: "{chromPath}"'
            assert all(chromData.iloc[:, 0].diff()[1:] > 0), assert_msg

            assert_msg = f'found unsorted file: "{chromPath}"'
            assert all(chromData.iloc[:, 1].diff()[1:] >= 0), assert_msg

            oligoLengthRange = self.get_oligo_length_range()
            oligoLengthList = chromData.iloc[:, 1] - chromData.iloc[:, 0]
            assert_msg = f'oligo too small for ".config" in "{chromPath}"'
            assert all(oligoLengthList >= oligoLengthRange[0]), assert_msg
            assert_msg = f'oligo too big for ".config" in "{chromPath}"'
            assert all(oligoLengthList <= oligoLengthRange[1]), assert_msg

            if self.has_overlaps():
                assert_msg = f'overlaps status mismatch in "{chromPath}"'
                assert self.check_overlaps(), assert_msg

            if self.has_sequences():
                assert_msg = f'missing sequence columns in "{chromPath}"'
                assert chromData.shape[1] >= 3, assert_msg

            if self.hasNetwork and self.has_sequences():
                for i in range(chromData.shape[0]):
                    chromStart, chromEnd, sequence = tuple(
                        chromData.iloc[i, :3].tolist())

                    assert_msg = 'sequence length does not match oligo'
                    assert_msg += f' (#{i}) length'
                    assert len(sequence) == chromEnd-chromStart, assert_msg

                    assert_status, msg = fp.web.check_sequence(
                        (chrom, chromStart, chromEnd), sequence,
                        self.get_reference_genome(),
                        UCSC_DAS_URI = self.UCSC_DAS_URI)
                    assert_msg = f'sequence of oligo #{i} does not match'
                    assert_msg += ' UCSC' + msg
                    assert assert_status, assert_msg
            
            if self.hasNetwork:
                chromSizeCheck = fp.web.check_chromosome_size(
                    chrom, chromData.iloc[-1, 1],
                    self.get_reference_genome(),
                    UCSC_DAS_URI = self.UCSC_DAS_URI)
                assert_msg = f'chromosome size not respected: "{chromPath}"'
                assert chromSizeCheck, assert_msg

            self.chromData[chrom] = chromData

class OligoProbe(object):
    """Class for probe management."""

    def __init__(self, chrom, oligos, database):
        super(OligoProbe, self).__init__()
        self.chrom = chrom
        self.oligoData = oligos
        self.refGenome = database.get_reference_genome()
        self.size = self.get_probe_size()
        self.spread = self.get_probe_spread()

    def get_probe_centrality(self, region):
        '''Calculate centrality, as location of the probe midpoint relative to
        the region midpoint. 1 when overlapping, 0 when the probe midpoint is
        at either of the region extremities.'''
        probe_halfWidth = self.size / 2
        region_halfWidth = (region[2] - region[1]) / 2
        probe_midPoint = self.oligoData.iloc[:, 0].min() + probe_halfWidth
        region_midPoint = region[1] + region_halfWidth
        centrality = (region_halfWidth - abs(
            region_midPoint - probe_midPoint)) / region_halfWidth
        return centrality

    def get_probe_size(self):
        '''Probe size, defined as difference between start of first oligo
        and end of the last one.'''
        return self.oligoData.iloc[:, 1].max() - self.oligoData.iloc[:, 0].min()

    def get_probe_spread(self):
        '''Probe spread, as the inverse of the standard deviation of the
        distance between consecutive oligos, calculated from their start
        position, disregarding oligo length.'''
        std = np.std(np.diff(self.oligoData.iloc[:, 1]))
        return np.inf if 0 == std else 1/std

    def describe(self, region, path = None):
        '''Builds a small pd.DataFrame describing a probe.'''
        description = pd.DataFrame.from_dict({
            'chrom' : [region[0]],
            'chromStart' : [self.oligoData.iloc[:, 0].min()],
            'chromEnd' : [self.oligoData.iloc[:, 1].max()],
            'centrality' : [self.get_probe_centrality(region)],
            'size' : [self.size],
            'spread' : [self.spread]
        })

        if not type(None) == type(path):
            config = configparser.ConfigParser()
            config['REGION'] = {
                'chrom' : region[0],
                'chromStart' : region[1],
                'chromEnd' : region[2]
            }
            config['PROBE'] = {
                'chrom' : description['chrom'].values[0],
                'chromStart' : description['chromStart'].values[0],
                'chromEnd' : description['chromEnd'].values[0],
                'nOligo' : self.oligoData.shape[0]
            }
            config['FEATURES'] = {
                'centrality' : description['centrality'].values[0],
                'size' : description['size'].values[0],
                'spread' : description['spread'].values[0]
            }
            with open(path, 'w+') as OH:
                config.write(OH)

        return description

    def get_fasta(self, path = None):
        fasta = ""
        for i in self.oligoData.index:
            oligo = self.oligoData.loc[i, :]
            chromStart, chromEnd, sequence = oligo[:3]
            fasta += f'> oligo_{i} [{self.refGenome}]'
            fasta += f'{self.chrom}:{chromStart}-{chromEnd}\n'
            fasta += f'{sequence}\n'

        if not type(None) == type(path):
            assert os.path.isdir(os.path.dirname(path))
            with open(path, 'w+') as OH:
                OH.write(fasta)

        return fasta

    def get_bed(self, path = None):
        bed = f'track description="ref:{self.refGenome}"\n'
        for i in self.oligoData.index:
            oligo = self.oligoData.loc[i, :]
            chromStart, chromEnd, sequence = oligo[:3]
            bed += f'{self.chrom}\t{chromStart}\t{chromEnd}\toligo_{i}\n'

        if not type(None) == type(path):
            assert os.path.isdir(os.path.dirname(path))
            with open(path, 'w+') as OH:
                OH.write(bed)

        return bed

    def plot(self, outputDir):
        assert os.path.isdir(outputDir), f'folder not found: "{outputDir}"'

class ProbeFeatureTable(object):
    """docstring for ProbeFeatureTable"""

    FEATURE_SORT = {
        'centrality' : {'ascending':False},
        'size' : {'ascending':True},
        'spread' : {'ascending':True},
    }

    def __init__(self, candidateList, queried_region, verbose = False):
        super(ProbeFeatureTable, self).__init__()
        
        self.data = []
        candidateList = tqdm(candidateList) if verbose else candidateList
        for candidate in candidateList:
            self.data.append(candidate.describe(queried_region))
        self.data = pd.concat(self.data)
        self.data.index = range(self.data.shape[0])

        self.discarded = None
    
    def filter(self, feature, thr):
        ''''''
        assert_msg = f'fetature "{feature}" not recognized.'
        assert feature in self.FEATURE_SORT.keys(), assert_msg

        if not type(None) == type(self.discarded):
            self.data = pd.concat([self.discarded, self.data])

        self.rank(feature)

        best_feature = self.data[feature].values[0]
        feature_delta = best_feature * thr
        feature_range = (best_feature-feature_delta, best_feature+feature_delta)

        discardCondition = [self.data[feature] < feature_range[0]]
        discardCondition.append(self.data[feature] > feature_range[1])
        discardCondition = np.logical_or(*discardCondition)
        self.discarded = self.data.loc[discardCondition, :]
        self.data = self.data.loc[np.logical_not(discardCondition), :]

    def rank(self, feature):
        self.data = self.data.sort_values(feature,
            ascending = self.FEATURE_SORT[feature]['ascending'])

# END ==========================================================================

################################################################################
