---
title: "iFISH-probe-design Usage"
---

# How to run iFISH-probe-design

## Web interface

For more details, check the [web interface page](https://ggirelli.github.io/fish-prode/web_interface).

## Command line

`iFISH-probe-design` can also be run from command line by running the `fprode_dbquery` script, which allows to **identify the best FISH probe** in a specific genomic region. Specifically, it provides a number of candidates from which the user can choose its favorite. If we run `fprode_dbquery -h` we get a useful recap of all the options:

```
usage: fprode_dbquery [-h] [--description descr] [--feat_order fo]
                      [--f1_thr ft] [--min_d md] [--n_oligo no]
                      [--n_probes np] [--max_probes mp] [--win_shift ws]
                      [-o od] [-f [F]]
                      id name chr start end db

Query database for a FISH probe.

positional arguments:
  id                   Query ID.
  name                 Query name.
  chr                  Chromosome in "ChrXX" format.
  start                Probe range starting position.
  end                  Probe range ending position.
  db                   Database folder path.

optional arguments:
  -h, --help           show this help message and exit
  --description descr  Query description
  --feat_order fo      Comma-separated features.
  --f1_thr ft          Threshold of first feature filter, used to identify a
                       range around the best value. It's the percentage range
                       around it. Accepts values from 0 to 1.
  --min_d md           Minimum distance between consecutive oligos.
  --n_oligo no         Number of oligos per probe.
  --n_probes np        Number of probes to design.
  --max_probes mp      Maximum number of output probe candidates. Set to "-1"
                       to retrieve all candidates.
  --win_shift ws       Window size fraction for shifting the windows.
  -o od, --outdir od   Query output directory.
  -f [F]               Force overwriting of the query if already run.
```

Probe characteristics
---------------------

The script focuses on three possible probe characteristics:

* **Size** (![I_i]). The size of the genomic regione covered by the probe. It is calculated as the difference between the end position of the last ![k]-mer (![E]) and the start position of the first ![k]-mer (![S]).

![Iiform]

* **Centrality** (![C_i]). It measures how centrally the probe is located in the specified Genomic Region of Interest (GRoI). Specifically, it takes values between 0 and 1, where 1 means perfectly central and 0 means perfectly borderline. Mathematically speaking, if ![S_g] and ![E_g] are respectively the start and end position of the GRoi, then

![MMCform]

With ![M_g] and ![M_i] being the middle points of the GRoI and of the ![i]-th probe, respectively, and ![dab] being the distance between the points `A` and `B`.

* **Spread** (![P_i]). It measures how homogeneously the oligomers are spread over the probe. It is basically the inverse of the consecutive-mers distance's standard deviation. Thus, the larger ![P_i], the more homogeneously the oligomers are spread.

![UPform]

It is important to note how size and spread need to be minimized, while centrality should be maximized.

Probe set characteristics
-------------------------

When run with `--n_probes` higher than 1 (default), the script calculates the characteristics of the probe sets, specifically, the *spread*-like measure calculated for every probe set aims at identifying the probe set with the most homogeneous probes in term of distribution and size. Thus, given ![S_i] and ![E_i] as the start and end of ![i]-th probe, we can define mean (![U]) and standard deviation (![T]) of the size and distribution of the probes:

![U_S]

![T_S]

![U_D]

![T_D]

Then, the *spread*-like measure (![P]) will be the inverse of the averaged standard deviations:

![revP]

Single Probe Algorithm
----------------------

The algorithm behind the single probe design considers a probe candidate as a set of ![N_O] consecutive oligomers (or ![k]-mers), in the genomic region of interest. Two ![k]-mers are considered **consecutive** when there are no other ![k]-mers between them.

It starts by checking that the number of requested ![k]-mers can actually fit the specified GRoI. Otherwise, it throws an error. Keeping in mind that the ``uniqueOligo`` pipeline forces a minimum distance ![min_d] between consecutive ![k]-mers, the minimum size of a GRoI is

![minIG]

If the query passes the first test, the tool proceeds with the generation of all probe candidates ![C]. This is achieved by ![N_O] grouping consecutive ![k]-mers in ![C].

![Ciform]

Where ![O_i] is the ![i]-th ![k]-mers in the GRoI and ![C_i] is the ![i]-th probe candidate. If the GRoI has ![N_G] ![k]-mers, then ![Nform] probe candidates are generated.

The algorithms requires to rank the probe characteristics (size, centrality, and spread) in so-called 1st, 2nd and 3rd *features* (![f_1], ![f_2], and ![f_3]).

![best1]
![best2]

Then, the 1st feature is calculated for every probe candidate ![C] and the best probe candidate is identified. An interval around the best candidate 1st feature value is calculated using the user-provided threshold ![t].

![Iform]

Every candidate probe ![C_i] with an ![fnot] is discarded.

Then, ![f_2] and ![f_3] are calculated for every remaining probe candidate. The candidates are ranked based on ![f_2] \(with the `best` on top) and returned as the output.

The tool also produces plots to easily understand how the probe is structured.

Multi Probe Algorithm
=====================

When asked to design ![N] probes, the algorithm works by:

1. Split the region of interest in ![Nplus1] windows.
2. Discard the last window.
3. Run the single-probe design algorithm in every window and identify the best probe based on the provided settings.
4. Shift the windows of ![shift] and repeat step 3. In other words, ![W_S] should be treated as a fraction of the window size: ![WS_in]
5. Repeat step 3-4 until the end of the region of interest is found.
6. Calculate a *spread*-like measure (described below) for every evaluated window set, i.e., for every candidate probe set.
7. Rank the candidate probe set based on the *spread* measure.




[k]: http://chart.apis.google.com/chart?cht=tx&chl=k
[i]: http://chart.apis.google.com/chart?cht=tx&chl=i
[t]: http://chart.apis.google.com/chart?cht=tx&chl=t
[S]: http://chart.apis.google.com/chart?cht=tx&chl=S
[E]: http://chart.apis.google.com/chart?cht=tx&chl=E
[C]: http://chart.apis.google.com/chart?cht=tx&chl=C
[I_i]: http://chart.apis.google.com/chart?cht=tx&chl=I_i
[C_i]: http://chart.apis.google.com/chart?cht=tx&chl=C_i
[M_g]: http://chart.apis.google.com/chart?cht=tx&chl=M_g
[M_i]: http://chart.apis.google.com/chart?cht=tx&chl=M_i
[P_i]: http://chart.apis.google.com/chart?cht=tx&chl=P_i
[S_g]: http://chart.apis.google.com/chart?cht=tx&chl=S_g
[E_g]: http://chart.apis.google.com/chart?cht=tx&chl=E_g
[N_O]: http://chart.apis.google.com/chart?cht=tx&chl=N_O
[f_1]: http://chart.apis.google.com/chart?cht=tx&chl=f_1
[f_2]: http://chart.apis.google.com/chart?cht=tx&chl=f_2
[f_3]: http://chart.apis.google.com/chart?cht=tx&chl=f_3
[dab]: http://chart.apis.google.com/chart?cht=tx&chl=d(A,B)
[min_d]: http://chart.apis.google.com/chart?cht=tx&chl=min_d
[O_i]: http://chart.apis.google.com/chart?cht=tx&chl=O_i
[N_G]: http://chart.apis.google.com/chart?cht=tx&chl=N_G
[fnot]: http://chart.apis.google.com/chart?cht=tx&chl=f_{1,i}\notin{I_{f_1}}
[minIG]: http://mathurl.com/y9kfy2az.png
[Ciform]: http://mathurl.com/yc9to77j.png
[best1]: http://mathurl.com/y8jsn7k2.png
[best2]: http://mathurl.com/y8sh9pos.png
[Iform]: http://mathurl.com/yaebla63.png
[Nform]: http://mathurl.com/y9aorugn.png
[Iiform]: http://chart.apis.google.com/chart?cht=tx&chl=I_i=E_i-S_i
[MMCform]: http://mathurl.com/yaq6xfzw.png
[UPform]: http://mathurl.com/y74watg9.png

[N]: http://chart.apis.google.com/chart?cht=tx&chl=N
[P]: http://chart.apis.google.com/chart?cht=tx&chl=P
[T]: http://chart.apis.google.com/chart?cht=tx&chl=T
[U]: http://chart.apis.google.com/chart?cht=tx&chl=U
[E_i]: http://chart.apis.google.com/chart?cht=tx&chl=E_i
[S_i]: http://chart.apis.google.com/chart?cht=tx&chl=S_i
[U_S]: http://mathurl.com/yb9tlvfn.png
[T_S]: http://mathurl.com/y7qkx93a.png
[U_D]: http://mathurl.com/y7oadht7.png
[T_D]: http://mathurl.com/y947tun5.png
[revP]: http://mathurl.com/y8qm34ln.png

[Nplus1]: http://mathurl.com/y7cwkfg5.png
[shift]: http://mathurl.com/ybje72uo.png
[W_S]: http://chart.apis.google.com/chart?cht=tx&chl=W_S
[WS_in]: http://mathurl.com/y8p28ojl.png