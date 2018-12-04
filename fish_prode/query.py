# -*- coding: utf-8 -*-

'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
@description: methods related to database query.
'''



# ==============================================================================

import matplotlib
matplotlib.use('svg')
import matplotlib.pyplot as plt

import configparser
import fish_prode as fp
import numpy as np
import os
import pandas as pd
from tqdm import tqdm

class OligoDatabase(object):
    """FISH-ProDe Oligonucleotide Database class."""

    def __init__(self, dbDirPath, hasNetwork = True,
        UCSC_DAS_URI = fp.web.UCSC_DAS_URI):
        super(OligoDatabase, self).__init__()
        self.dirPath = dbDirPath
        self.hasNetwork = hasNetwork
        self.UCSC_DAS_URI = UCSC_DAS_URI
        self.chromData = {}

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

    def has_chromosome(self, chrom):
        return chrom in os.listdir(self.dirPath)

    def read_chromosome(self, chrom):
        assert self.has_chromosome(chrom)
        
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

    def read_all_chromosomes(self, verbose):
        chromList = [d for d in os.listdir(self.dirPath)
            if not d.startswith('.')]
        assert 1 < len(chromList), "no chromosome files found in {self.dirPath}"
        chromList = tqdm(chromList) if verbose else chromList

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
        self.spread = self.get_probe_spread()

    def __str__(self):
        s  = f'[{self.refGenome}]'
        s += f'{self.chrom}:{self.chromStart}-{self.chromEnd};'
        s += f' oligoSpread: {self.spread}'
        return s

    def asDataFrame(self, region = None):
        if type(None) == type(region):
            return pd.DataFrame.from_dict({
                'chrom' : [self.chrom],
                'chromStart' : [self.chromStart],
                'chromEnd' : [self.chromEnd],
                'refGenome' : [self.refGenome],
                'midpoint' : [self.midpoint],
                'size' : [self.size],
                'spread' : [self.spread]
            })
        else:
            return pd.DataFrame.from_dict({
                'chrom' : [self.chrom],
                'chromStart' : [self.chromStart],
                'chromEnd' : [self.chromEnd],
                'refGenome' : [self.refGenome],
                'midpoint' : [self.midpoint],
                'size' : [self.size],
                'spread' : [self.spread],
                'regChromStart' : region[0],
                'regChromEnd' : region[1]
            })

    def get_probe_centrality(self, region):
        '''Calculate centrality, as location of the probe midpoint relative to
        the region midpoint. 1 when overlapping, 0 when the probe midpoint is
        at either of the region extremities.'''
        region_halfWidth = (region[2] - region[1]) / 2
        region_midPoint = region[1] + region_halfWidth
        centrality = (region_halfWidth - abs(
            region_midPoint - self.midpoint)) / region_halfWidth
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

    def _plot_region(self, outputDir, region):
        fig = plt.figure()

        chrom, start, stop = region
        plt.plot([start, stop], [0, 0], 'k', linewidth = 4.0, label = 'Genome')
        plt.plot([start + (stop-start)/2., start + (stop-start)/2.],
            [-1, 1], 'r--', label = 'Window center')

        plt.plot([self.chromStart, self.chromEnd], [0, 0],
            'c-', linewidth = 4.0, label = 'Probe')
        plt.plot([self.chromStart+self.size/2., self.chromStart+self.size/2.],
            [-1, 1], 'c--',label = 'Probe center')

        plt.gca().axes.get_yaxis().set_visible(False)
        plt.suptitle('%s:%d-%d' % (chrom, start, stop))
        plt.xlabel('genomic coordinate [nt]')
        plt.legend(fontsize = 'small', loc = 'best')

        plt.savefig(os.path.join(outputDir, 'window.png'),
            format = 'png', bbox_inches = 'tight')
        plt.close(fig)

    def _plot_oligo(self, outputDir):
        fig = plt.figure(figsize = (20, 5))
        genome_handle, = plt.plot([self.chromStart, self.chromEnd],
            [0, 0], 'k', linewidth = 4.0, label = 'Genome')

        for i in self.oligoData.index:
            oligo = self.oligoData.loc[i, :]
            oligo_midpoint = (oligo['chromStart'] + oligo['chromStart']) / 2.
            oligo_handle, = plt.plot([oligo['chromStart'], oligo['chromEnd']],
                [0, 0], 'c', linewidth = 2.0, label = 'Oligo')
            oligoCenter_handle, = plt.plot(
                [oligo_midpoint, oligo_midpoint],
                [-.1, .1], 'c:', label = 'Oligo center')

        plt.gca().axes.get_yaxis().set_visible(False)
        plt.ylim((-.5, .5))

        plt.gca().axes.get_xaxis().set_ticks(list(range(
            self.chromStart, self.chromEnd,
            int((self.chromEnd-self.chromStart)/5.))))

        plt.legend(handles = [genome_handle, oligo_handle, oligoCenter_handle],
            fontsize = 'small', loc = 'best')
        plt.suptitle((f'{self.chrom}:{self.chromStart}-{self.chromEnd}'))
        plt.xlabel('genomic coordinate [nt]')

        plt.savefig(os.path.join(outputDir, 'probe.png'),
            format = 'png', bbox_inches = 'tight')
        plt.close(fig)

    def _plot_oligo_distr(self, outputDir):
        fig = plt.figure()

        plt.plot(
            [0, self.oligoData.shape[0]-1],
            [self.chromStart, self.chromEnd], 'k-',
            label = 'Homogeneous distribution')
        plt.plot(
            list(range(self.oligoData.shape[0])),
            self.oligoData['chromStart'].values,
            'r.', label = 'Oligo')

        plt.suptitle(f'{self.chrom}:{self.chromStart}-{self.chromEnd}')
        plt.xlabel('oligo number')
        plt.ylabel('genomic coordinate [nt]')
        plt.legend(fontsize = 'small', loc = 'best')

        plt.savefig(os.path.join(outputDir, 'oligo.png'), format = 'png')
        plt.close(fig)

    def _plot_oligo_distance(self, outputDir):
        fig = plt.figure()

        startPositions = self.oligoData.iloc[1:, 0].values
        endPositions = self.oligoData.iloc[:-1, 1]
        diffs =  startPositions - endPositions
        plt.hist(diffs, density = 1, facecolor = 'green', alpha = .5)
        density = fp.stats.calc_density(diffs, alpha = .5)
        plt.plot(density['x'].tolist(), density['y'].tolist(), 'b--',
            label = 'Density distribution')

        plt.suptitle(f'{self.chrom}:{self.chromStart}-{self.chromEnd}')
        plt.xlabel('Distance between consecutive oligos [nt]')
        plt.ylabel('Density')
        plt.legend(fontsize = 'small', loc = 'best')

        plt.savefig(os.path.join(outputDir, 'distance.png'), format = 'png')
        plt.close(fig)

    def plot(self, outputDir, region):
        assert os.path.isdir(outputDir), f'folder not found: "{outputDir}"'
        self._plot_region(outputDir, region)
        self._plot_oligo(outputDir)
        self._plot_oligo_distr(outputDir)
        self._plot_oligo_distance(outputDir)

class ProbeFeatureTable(object):
    FEATURE_SORT = {
        'centrality' : {'ascending':False},
        'size' : {'ascending':True},
        'spread' : {'ascending':False},
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

    def reset(self):
        self.data = pd.concat([self.discarded, self.data])
        self.discarded = None
        self.data.sort_index(inplace = True)

    def keep(self, condition, cumulative = False):
        if not cumulative:
            self.reset()
        self.discarded = self.data.loc[np.logical_not(condition), :]
        self.data = self.data.loc[condition, :]

    def filter(self, feature, thr, cumulative = False):
        ''''''
        assert_msg = f'fetature "{feature}" not recognized.'
        assert feature in self.FEATURE_SORT.keys(), assert_msg

        if not cumulative:
            self.reset()

        self.rank(feature)

        best_feature = self.data[feature].values[0]
        feature_delta = best_feature * thr
        feature_range = (best_feature-feature_delta, best_feature+feature_delta)

        discardCondition = [self.data[feature] < feature_range[0]]
        discardCondition.append(self.data[feature] > feature_range[1])
        discardCondition = np.logical_or(*discardCondition)
        self.discarded = self.data.loc[discardCondition, :]
        self.data = self.data.loc[np.logical_not(discardCondition), :]

        return (feature_range, feature)

    def rank(self, feature):
        self.data = self.data.sort_values(feature,
            ascending = self.FEATURE_SORT[feature]['ascending'])

class GenomicWindow(object):
    def __init__(self, start, size):
        super(GenomicWindow, self).__init__()
        self.chromStart = start
        self.chromEnd = start + size
        self.midpoint = (self.chromStart + self.chromEnd) / 2
        self.size = size
        self.probe = None

    def __str__(self):
        s  = f'GenomicWindow:{self.chromStart}-{self.chromEnd}\n'
        s += f' Probe: {self.probe}'
        return s

    def has_probe(self):
        return type(None) != type(self.probe)

    def shift(self, n):
        return GenomicWindow(self.chromStart + n, self.size)

class GenomicWindowList(object):
    data = []

    def __init__(self, windows = None):
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

    def add(self, start, size):
        self.data.append(GenomicWindow(start, size))

    def count_probes(self):
        return sum([1 for w in self if w.has_probe()])

    def shift(self, n):
        return GenomicWindowList([window.shift(n) for window in self.data])

    def sort(self):
        midpointList = np.array([w.midpoint for w in self.data])
        self.data = [self.data[i] for i in np.argsort(midpointList)]

    def calc_probe_size_and_spread(self):
        if 3 < self.count_probes():
            return np.nan

        probeData = pd.concat([w.probe.asDataFrame((w.chromStart, w.chromEnd))
            for w in self if type(None) != type(w.probe)])
        size_std = probeData['size'].values.std()
        probe_spread = np.std(probeData['chromStart'].values[1:] - 
            probeData['chromEnd'].values[:-1])
        return 2 / (size_std + probe_spread)

    def asDataFrame(self):
        starts = []
        ends = []
        sizes = []
        for window in self:
            starts.append(window.chromStart)
            ends.append(window.chromEnd)
            sizes.append(window.size)
        return pd.DataFrame.from_dict({
            'chromStart' : starts,
            'chromEnd' : ends,
            'size' : sizes
        })

# END ==========================================================================

################################################################################
