---
title: ifpd scripts
---

<!-- MarkdownTOC -->

- [`ifpd mkdb`](#ifpd-mkdb)
- [`ifpd dbchk`](#ifpd-dbchk)
- [`ifpd query probe`](#ifpd-query-probe)
- [`ifpd query set`](#ifpd-query-set)
- [`ifpd serve`](#ifpd-serve)

<!-- /MarkdownTOC -->

All `ifpd` commands are accessible via the `ifpd` keyword. For each command, you can access its help page by using the `-h` option. Moreover, a selection of examples is available in [the corresponding page]({{ site.baseurl }}/examples).

## `ifpd mkdb`

This script takes a BED-like file of four (4) columns (`chromosome`, `start` position, `end` position, and `sequence`), and generates a [database]({{ site.baseurl }}/database) folder in a format compatible with the rest of `ifpd`'s scripts.

The minimum input comprises the input file path and a name for the new database. We recommend providing also a reference genome label (via `--refGenome`), which is retained in the database config file for trackability.

As explained in the [database]({{ site.baseurl }}/database) page, the input file is expected to respect the UCSC BED format pertaining the indexing of genomic coordinates. If your input file specifies regions with both `start` and `end` positions being inclusive, you can use the `--increment-chrom-end` option to convert it to the appropriate format.

## `ifpd dbchk`

This script checks a database for proper formatting and compatibility with the `ifpd` package.

## `ifpd query probe`

This script queries a database to design a single iFISH probe, using the algorithm explained in [the corresponding page]({{ site.baseurl }}/algorithms#single-probe-design).

The minimum input comprises (in order):

1. `database`: the path to the database folder.
2. `chrom`: the chromosome (or database feature) to be queried.
3. `outputDirectory`: the path to the query output folder.

Some optional parameters, used as detailed in the algorithms page, are also available.

* The extremes of the region of interest (via `--region start end`). If skipped, or if `start` and `end` coincide, the whole feature is queried.
* The `--order` option allows to provide the features priority order, by providing a space-separated list of features (at least 2). For example: `--order homogeneity size centrality`.
* The `--filter-thr` option specifies the fraction used to define the range in the filtering step (*F*). This should be a fraction (from 0 to 1), and defaults to 0.1.
* The `--n-oligo` to specify the number of oligos desired in a probe. The default is 48.
* `--max-probes` to specify the maximum number of probe candidates you want as output. The default (`-1`) outputs all candidates.

For security reasons, if the specified `outputDirectory ` already exists, the script triggers an `AssertError`. To force this through, use the `-f` option. But keep in mind that this will overwrite the specified `outputDirectory`, deleting its whole content.

Note also that, by default, if the number of oligos in the specified region of interest is lower than the number requested via `--n-oligo`, the largest probe possible is generated. If a smaller probe would not be useful, use `--exact-n-oligo` to stop the execution earlier.

## `ifpd query set`

This script queries a database to design a spotting iFISH probe, using the algorithm explained in [the corresponding page]({{ site.baseurl }}/algorithms#spotting-probe-design).

The minimum input comprises (in order):

1. `database`: the path to the database folder.
2. `chrom`: the chromosome (or database feature) to be queried.
4. `outputDirectory`: the path to the query output folder.
3. `nProbes`: the number of desired probes for the spotting design.

Some optional parameters, used as detailed in the algorithms page, are also available.

* The extremes of the region of interest (via `--region start end`). If skipped, or if `start` and `end` coincide, the whole feature is queried.
* The `--order` option allows to provide the features priority order, by providing a space-separated list of features (at least 2). For example: `--order homogeneity size centrality`.
* The `--filter-thr` option specifies the fraction used to define the range in the filtering step (*F*). This should be a fraction (from 0 to 1), and defaults to 0.1.
* The `--n-oligo` to specify the number of oligos desired in a probe. The default is 48.
* `--max-sets` to specify the maximum number of probe candidates you want as output. The default (`-1`) outputs all candidates.
* `-t` to specify a number of threads to use, for parallelized computation.
* Internet connection is required when designing a chromosome-spotting probe, to retrieve the chromosome size. If internet connection is not available, use the `--no-net` to use the end of the last oligo in a chromosome as chromosome size.

For security reasons, if the specified `outputDirectory ` already exists, the script triggers an `AssertError`. To force this through, use the `-f` option. But keep in mind that this will overwrite the specified `outputDirectory`, deleting its whole content.

Note also that, by default, if the number of oligos in the specified region of interest is lower than the number requested via `--n-oligo`, the largest probe possible is generated. If a smaller probe would not be useful, use `--exact-n-oligo` to stop the execution earlier.

## `ifpd serve`

This script can be used to run the `ifpd` [web interface]({{ site.baseurl }}/interface) on your own computer. If run without any parameters, it serves the interface at the `0.0.0.0:8080` address. URL and port can be customized using the `-u` and `-p` options, respectively.

The interface requires also a `static` folder (by default created in the package installation path), where databases and queries are stored. It is highly advised to specify a custom static folder path. The structure of the static folder, created when running `ifpd serve` the first time, is the following:

```
static_folder
    ┣ db
    ┃  ┣ folder_db1
    ┃  ┣ folder_db2
    ┃  ┣ ...
    ┃  ┗ folder_dbN
    ┗ query
       ┣ folder_query1
       ┣ folder_query2
       ┣ ...
       ┣ folder_queryN
       ┣ query1.config
       ┣ query2.config
       ┣ ...
       ┗ queryN.config
```

Finally, with the `-m` option one can specify an email address to contact in case a query crashes or times out.

Additional options like `-H`, `-T` and `-R` are required only for advanced customization. An example of which is available at the [iFISH4U](http://github.com/ggirelli/iFISH4U) repository.
