"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import numpy as np  # type: ignore
from scipy import stats as spStats  # type: ignore


def calc_density(data, **kwargs):
    """Calculate the Gaussian KDE of the provided data series."""
    sigma = 0.2 if "sigma" not in list(kwargs.keys()) else kwargs["sigma"]
    nbins = 1000 if "nbins" not in list(kwargs.keys()) else kwargs["nbins"]

    # If only one nucleus was found
    if 1 == len(data):
        f = eval(f"lambda x: 1 if x == {data[0]} else 0")
        f = np.vectorize(f)
        return {"x": np.array([data[0]]), "y": np.array([1]), "f": f}

    data = data[np.logical_not(np.isnan(data))]
    density = spStats.gaussian_kde(data)
    density.covariance_factor = lambda: sigma
    density._compute_covariance()
    return {
        "x": np.linspace(min(data), max(data), nbins),
        "y": density(np.linspace(min(data), max(data), nbins)),
        "f": density,
    }
