# -*- coding: utf-8 -*-

'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
@description: statistical methods.
'''

# ==============================================================================

import numpy as np
from scipy import stats as spStats

def calc_density(data, **kwargs):
    '''Calculate the Gaussian KDE of the provided data series.'''
    sigma = .2 if not 'sigma' in list(kwargs.keys()) else kwargs['sigma']
    nbins = 1000 if not 'nbins' in list(kwargs.keys()) else kwargs['nbins']

    # If only one nucleus was found
    if 1 == len(data):
        f = eval(f'lambda x: 1 if x == {data[0]} else 0')
        f = np.vectorize(f)
        return({
            'x' : np.array([data[0]]),
            'y' : np.array([1]), 'f' : f
        })

    data = data[np.logical_not(np.isnan(data))]
    density = spStats.gaussian_kde(data)
    density.covariance_factor = lambda : sigma
    density._compute_covariance()
    return({
        'x' : np.linspace(min(data), max(data), nbins),
        'y' : density(np.linspace(min(data), max(data), nbins)),
        'f' : density
    })


# END ==========================================================================

################################################################################
