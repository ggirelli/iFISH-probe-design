Probe designer v0.0.1
=====================

This service contains the tools to enquire databases of FISH-compatible genomically unique oligomeres, generated with the ``uniqueOligo`` pipeline. Every database is generated with a different set of parameters, representing more and less restrictive definitions of *uniqueness*. The stricter the definition, the less a-specific signal is expected when using them in a FISH probe.

With **enquiring** or **querying** the database, we mean to extract a set of oligomers that can be used as an oligo-based FISH probe. Thus, please note that when we refer to **FISH probe** in this documentation we mean a set of oligomers.

Specifically, the tools/options here described are the following:

* ``Single query``. Design a single FISH probe by filling an online form. The features that are taken into consideration during the probe design are its size in nt, how homogeneously its oligomers are spread and how centrally the probe is located in the queried region.
* ``Single queries``. Perform multiple single FISH probe designs by uploading a spreadsheet file, without having to fill up the form (see above) multiple times.
* ``Multi query``. Design a set of homogeneously spread probes in a given genomic region (still in development).

Of course, the querying results can be easily navigate from the ``index``.

.. toctree::
   :maxdepth: 2
   :caption: Options
   :name: options

   probe_designer/index
   probe_designer/multi_query
   probe_designer/single_query
   probe_designer/single_queries


.. toctree::
   :maxdepth: 2
   :caption: Pages
   :name: pages

   probe_designer/query
   probe_designer/candidate


.. toctree::
   :maxdepth: 2
   :caption: For developers
   :name: devel

   probe_designer/dev_setup
   probe_designer/dev_database
   probe_designer/dev_query


.. toctree::
   :maxdepth: 2
   :caption: Others
   :name: pd_others

   probe_designer/changelog
   probe_designer/todo
