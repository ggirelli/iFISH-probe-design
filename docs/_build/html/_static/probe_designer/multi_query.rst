Multi query
===========

This option allows to **design a set of homogeneously spread probes** in a specific genomic region. This tool requires the same input as the single-query one, plus: number of probes (:math:`N`) and window shift (:math:`W_S`). While the first is self-explanatory, being the number of probes to be designed, the second will become clearer after the algorithm is explained (see below).

When asked to design :math:`N` probes, the algorithm works by:

1. Split the region of interest in :math:`N+1` windows.
2. Discard the last window.
3. Run the single-probe design algorithm in every window and identify the best probe based on the provided settings.
4. Shift the windows of :math:`W_S * (E - S) / (N + 1)` and repeat step 3. In other words, :math:`W_S` should be treated as a fraction of the window size: :math:`W_S \in [0, 1]`
5. Repeat step 3-4 until the end of the region of interest is found.
6. Calculate a *spread*-like measure (described below) for every evaluated window set, i.e., for every candidate probe set.
7. Rank the candidate probe set based on the *spread* measure.

The *spread*-like measure calculated for every probe set aims at identifying the probe set with the most homogeneous probes in term of distribution and size. Thus, given :math:`S_i` and :math:`E_i` as the start and end of :math:`i`-th probe, we can define mean (:math:`U`) and standard deviation (:math:`T`) of the size and distribution of the probes:

$$ U_S = \\sum_{j=1}^{N}{\\frac{E_{j} - S_{j}}{N}} $$

$$ T_S = \\sqrt{\\sum_{j=1}^{N}{\\frac{(U_S - \\lvert E_{j} - S_{j}\\rvert )^2}{N}}} $$

$$ U_D = \\sum_{j=1}^{N - 1}{\\frac{S_{j+1} - E_{j}}{N - 1}} $$

$$ T_D = \\sqrt{\\sum_{j=1}^{N_O - 1}{\\frac{(U_D - \\lvert S_{j+1} - E_{j}\\rvert )^2}{N_O - 1}}} $$

Then, the *spread*-like measure (:math:`P`) will be the inverse of the averaged standard deviations:

$$ \\frac{1}{P} = \\frac{T_S + T_D}{2} $$