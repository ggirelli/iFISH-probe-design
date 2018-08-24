Single query
============

This option allows to **identify the best FISH probe** in a specific genomic region. Specifically, it provides a number of candidates from which the user can choose its favorite.

The form is divided into four panels:

* The **general** panel contains the query's ``name`` and ``description`` (quite self-explanatory).
* In the **where** panel the user can specify the **genomic region** of interest, with the ``chromosome``, ``start`` and ``end`` parameters (i.e., ``chr:start-end``). Moreover, it is possible to select the ``database`` from which to extract the oligomers. The choice of the database is critical, since it influences both the length of the oligomers and their definition of *uniqueness*.
* The **what** panel allows to specify how many ``oligomers`` the probe must have, and the maximum number of desired output candidates (``max output probes``). If this last parameter is set to ``-1``, all the candidates that were found will be reported. It is also possible to specify a ``threshold`` (from 0 to 1) used to define a range around the best value of the so-called *first feature*, which will be explained in detail in the **algorithm** section below.
* In the **advanced settings** the user can choose which, between **centrality**, **size** and **spread**, should be used as 1st, 2nd and 3rd feature, respectively. The meaning of these 3 features is explained in detail in the **algorithm** section below, together with the formal definition of the 3 measures.

Probe characteristics
---------------------

The tools focuses on three possible probe characteristics:

* **Size** (:math:`I_i`). The size of the genomic regione covered by the probe. It is calculated as the difference between the end position of the last :math:`k`-mer (:math:`E`) and the start position of the first :math:`k`-mer (:math:`S`).

$$I_i = E_i - S_i$$

* **Centrality** (:math:`C_i`). It measures how centrally the probe is located in the specified genomic region of interest (GRoI). Specifically, it takes values between 0 and 1, where 1 means perfectly central and 0 means perfectly borderline. Mathematically speaking, if :math:`S_g` and :math:`E_g` are respectively the start and end position of the GRoi, then

$$M_i = S_i + \\frac{E_i - S_i}{2}$$
$$M_g = S_g + \\frac{E_g - S_g}{2}$$
$$C_i = \\frac{\\left\| \\overline{S_g M_g} - \\overline{M_i M_g} \\right\|}{\\overline{S_g M_g}}$$

With :math:`M_g` and :math:`M_i` being the middle points of the GRoI and of the :math:`i`-th probe, respectively.

* **Spread** (:math:`P_i`). It measures how homogeneously the oligomers are spread over the probe. It is basically the inverse of the consecutive-mers distance's standard deviation. Thus, the larger :math:`P_i`, the more homogeneously the oligomers are spread.

$$ U_i = \\sum_{j=1}^{N_O - 1}{\\frac{S_{j+1} - E_{j}}{N_O - 1}} $$

$$ \\frac{1}{P_i} = \\sqrt{\\sum_{j=1}^{N_O - 1}{\\frac{(U - \\lvert S_{j+1} - E_{j}\\rvert )^2}{N_O - 1}}} $$

It is important to note how size and spread need to be minimized, while centrality should be maximized.

Algorithm
---------

The algorithm behind the single probe design considers a probe candidate as a set of :math:`N_O` consecutive oligomers (or :math:`k`-mers), in the genomic region of interest. Two :math:`k`-mers are considered **consecutive** when there are no other :math:`k`-mers between them.

It starts by checking that the number of requested :math:`k`-mers can actually fit the specified GRoI. Otherwise, it throws an error. Keeping in mind that the ``uniqueOligo`` pipeline forces a minimum distance :math:`min\_d` between consecutive :math:`k`-mers, the minimum size of a GRoI is

$$ min\\_{I_G} = k · N_O + min\\_d · (N_O - 1) $$

If the query passes the first test, the tool proceeds with the generation of all probe candidates :math:`C`. This is achieved by :math:`N_O` grouping consecutive :math:`k`-mers in :math:`C`.

$$ C_i = O_i, O_{i + 1}, ..., O_{i + N_O - 1} $$

Where :math:`O_i` is the :math:`i`-th :math:`k`-mers in the GRoI and :math:`C_i` is the :math:`i`-th probe candidate. If the GRoI has :math:`N_G` :math:`k`-mers, then :math:`N_G - N_O + 1` probe candidates are generated.

The algorithms requires to rank the probe characteristics (size, centrality, and spread) in so-called 1st, 2nd and 3rd *features* (:math:`f_1`, :math:`f_2`, and :math:`f_3`).

$$ \\operatorname{best}(f_x) = \\left\[ \\begin{array}{cc}
\\operatorname{max}(f_x) & \\operatorname{if} f_x \\in \\{\\operatorname{centrality}\\} \\\\
\\operatorname{min}(f_x) & \\operatorname{if} f_x \\in \\{\\operatorname{size}, \\operatorname{spread}\\} \\\\
\\end{array} \\right. $$

Then, the 1st feature is calculated for every probe candidate :math:`C` and the best probe candidate is identified. An interval around the best candidate 1st feature value is calculated using the user-provided threshold :math:`t`.

$$ I_{f_1} = [ \\operatorname{best}(f_1) - t·\\operatorname{best}(f_1), \\operatorname{best}(f_1) + t·\\operatorname{best}(f_1) ] $$

Every candidate probe :math:`C_i` with an :math:`f_{1,i} \notin I_{f_1}` is discarded.

Then, :math:`f_2` and :math:`f_3` are calculated for every remaining probe candidate. The candidates are ranked based on :math:`f_2` (with the :math:`\operatorname{best}` on top) and returned as the output.

The tool also produces plots to easily understand how the probe is structured. More details about the plots are available in the ``query`` and ``candidate`` pages.