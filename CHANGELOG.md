# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).



## Unreleased
### ...
- ...



## [2.0.1.post5] - 2019-02-04
### Fixed
- Changed links in headers for CORS.
- Changed routes to Probe design app for "/" management.



## [2.0.1.post4] - 2019-02-01
### Changed
- Now showing error log if a query crashes.



## [2.0.1.post3] - 2019-01-31
### Fixed
- Calculation of oligonucleotide midpoint for plotting.


## [2.0.1] - 2019-01-30
### Added
- Option for cookie consent banner.
- Menu advanced options.

### Changed
- Moved link to close bookmark alert to the right.
- Renamed `spread` feature to `homogeneity`.
- Made fields in query form responsiv.



## [2.0.0.post1] - 2019-01-25
### Added
- `bioext` module for biological file extension methods.
    + `UCSCbed` class to read files in UCSC bed format.
- `web` module for web-service related methods.
    + UCSC DAS server related methods.
- `query` module for query and database management.
    + Implemented oligo database class that asserts it when reading it.
- `stats` module for statistics-related methods.
- `fprode_mkdb` script: re-format a database to be compatible with FISH-ProDe.
    + List UCSC available reference genomes with `--list-refGenomes`.
    + `.config` file generated using the `configparser` package.
- `fprode_dbchk`: checks database integrity.
- Parallelization to probe set query script. (only local)

### Changed
- Renamed package to `ifpd`.
- Moved interface documents to separate sub-folder.
- Each database is structured as follows:
    + One file per chromosome, with the name being the same as the chromosome. One row per oligo and two columns: start and end position, as per the UCSC bed format standard. Also, a third (optional) column can be present, with the sequence of the oligo.
    + One `.config` file with the database details.
- Database query now split in two scripts (`fprode_dbquery_probe` and `fprode_dbquery_probeSet`), for single-probe and probe-set design.
    + Query-related methods moved to the `query` sub-module.
    + Query ID now handled server-side, for easier standalone script execution.
    + Region of interest now passed as `chrN:XXX,YYY`, for convenience.
    + Query name and description now handled only server-side, i.e., removed as input parameters of the query scripts.
- Refined user interface.
- Queue in web interface now reports region and isotimestamp for each queued query.
- Queries can be reached by knowing their ID only.
- Using newer version of JavaScript libraries.

### Removed
- `fprode_dbextract`
- Single probe batch query interface.
- Query table from interface.



## [1.1.0] - 2018-08-25
### Changed
- Refactored as Python package.



## [0.0.1] - 2017-08-06 - First release


[2.0.1] https://github.com/ggirelli/iFISH-probe-design/releases/tag/v2.0.1
[2.0.0.post1] https://github.com/ggirelli/iFISH-probe-design/releases/tag/v2.0.0.post1
[1.1.0] https://github.com/ggirelli/iFISH-Probe-Design/releases/tag/v1.1.0  
[0.0.1] https://github.com/ggirelli/iFISH-Probe-Design/releases/tag/v0.0.1  
