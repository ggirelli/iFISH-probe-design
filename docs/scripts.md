---
title: ifpd scripts
---

You can access the help page of each script by using the `-h` option. Moreover, a selection of examples is available in [the corresponding page]({{ site.baseurl }}/examples).

## `ifpd_mkdb`

This script takes a BED-like file of at least three columns (`chromosome`, `start` position, and `end` position), and generates a [database]({{ site.baseurl }}/database) folder in a format compatible with the rest of `ifpd`'s scripts. The input file can contain a fourth optional column with the `sequence` corresponding to each row's region. If that is the case, the sequence can be retained by using the `--retain-sequences`.

The minimum input comprises the BED-like file path, the corresponding reference genome, and a name for the new database. Importantly, the specified reference genome must be in an NCBI-compatible format and available at UCSC. Use the `--list-refGenomes` to show the list of available genomes.

If you want to use a genome available through a DAS server different from the UCSC one, you can specify the DAS server URL with the `--das-uri`. If you do not have internet connection, use the `--no-net` option.

As explained in the [database]({{ site.baseurl }}/database) page, the input BED-like file is expected to respect the UCSC BED format pertaining the indexing of genomic coordinates. If your input file specifies regions with both `start` and `end` positions being inclusive, you can use the `--increment-chrom-end` option to convert it to the appropriate format.

## `ifpd_dbchk`

This script checks a database for proper formatting and compatibility with the `ifpd` package. Some checks require internet connection. Use `--no-net` to skip them. Also, when a connection to the internet is available, use the `--check-seq` to verify that the sequences stored in the database are correct. This sequence-check step is skipped by default due to it being extremely slow.

## `ifpd_query_probe`

This script queries a database to design a single iFISH probe, using the algorithm explained in [the corresponding page]({{ site.baseurl }}/algorithms#single-probe-design).

The minimum input comprises (in order):

1. `region`: the genomic region of interest, in the following format: `chrN:XXX,YYY`.
2. `database`: the path to the database folder.
3. `outputDirectory`: the path to the query output folder.

Some optional parameters, used as detailed in the algorithms page, are also available.

* The `--order` option allows to provide the features priority order, by providing a space-separated list of features (at least 2). For example: `--order homogeneity size centrality`.
* The `--filter-thr` option specifies the fraction used to define the range in the filtering step (*F*). This should be a fraction (from 0 to 1), and defaults to 0.1.
* The `--n-oligo` to specify the number of oligos desired in a probe. The default is 48.
* `--max-probes` to specify the maximum number of probe candidates you want as output. The default (`-1`) outputs all candidates.

For security reasons, if the specified `outputDirectory ` already exists, the script triggers an `AssertError`. To force this through, use the `-f` option. But keep in mind that this will overwrite the specified `outputDirectory`, deleting its whole content.

## `ifpd_query_set`

This script queries a database to design a spotting iFISH probe, using the algorithm explained in [the corresponding page]({{ site.baseurl }}/algorithms#spotting-probe-design).

The minimum input comprises (in order):

1. `region`: the genomic region of interest, in the following format: `chrN:XXX,YYY`. Also, a chromosome-spotting probe can be designed by specifying a region as `chrN`.
2. `nProbes`: the number of desired probes for the spotting design.
3. `database`: the path to the database folder.
4. `outputDirectory`: the path to the query output folder.

Some optional parameters, used as detailed in the algorithms page, are also available.

* The `--order` option allows to provide the features priority order, by providing a space-separated list of features (at least 2). For example: `--order homogeneity size centrality`.
* The `--filter-thr` option specifies the fraction used to define the range in the filtering step (*F*). This should be a fraction (from 0 to 1), and defaults to 0.1.
* The `--n-oligo` to specify the number of oligos desired in a probe. The default is 48.
* `--max-sets` to specify the maximum number of probe candidates you want as output. The default (`-1`) outputs all candidates.
* `-t` to specify a number of threads to use, for parallelized computation.
* Internet connection is required when designing a chromosome-spotting probe, to retrieve the chromosome size. If internet connection is not available, use the `--no-net` to use the end of the last oligo in a chromosome as chromosome size.

For security reasons, if the specified `outputDirectory ` already exists, the script triggers an `AssertError`. To force this through, use the `-f` option. But keep in mind that this will overwrite the specified `outputDirectory`, deleting its whole content.

## `ifpd_serve`

This script can be used to run the `ifpd` [web interface]({{ site.baseurl }}/interface) on your own computer. If run without any parameters, it serves the interface at the `0.0.0.0:8080` address. URL and port can be customized using the `-u` and `-p` options, respectively.

The interface requires also a `static` folder (by default created in the package installation path), where databases and queries are stored. It is highly advised to specify a custom static folder path using the `-s` option. The structure of the static folder, created when running `ifpd_serve` the first time, is the following:

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
