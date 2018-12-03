# -*- coding: utf-8 -*-

'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
@description: methods related to database query.
'''

# DEPENDENCIES =================================================================

import os
import pandas as pd

# ==============================================================================

def get_probe_centrality(probe, region):
    ''''''
    pass

def get_pobe_size(probe):
    ''''''
    pass

def get_probe_spread(probe):
    ''''''
    pass

def describe_probe(probe, region):
    '''Builds a small pd.DataFrame describing a probe.'''
    return pd.DataFrame.from_dict({
        'chrom' : [region[0]],
        'chromStart' : [probe.iloc[:, 0].min()],
        'chromEnd' : [probe.iloc[:, 1].max()],
        'centrality' : [get_probe_centrality(probe, region)],
        'size' : [get_pobe_size(probe)],
        'spread' : [get_probe_spread(probe)]
    })

# END ==========================================================================

################################################################################
