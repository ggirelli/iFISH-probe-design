# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).



## Unreleased
### Added
- `bioext` sub-package for biological file extension methods.
    + `UCSCbed` class to read files in UCSC bed format.
- `web` sub-package for web-service related methods.
    + UCSC DAS server related methods.
- `fprode_mkdb` script: re-format a database to be compatible with FISH-ProDe.
    + List UCSC available reference genomes with `--list-refGenomes`.
    + `.config` file generated using the `configparser` package.
- `fprode_dbchk`: checks database integrity.

### Changed
- Moved interface documents to separate sub-folder.
- Each database is structured as follows:
    + One file per chromosome, with the name being the same as the chromosome. One row per oligo and two columns: start and end position, as per the UCSC bed format standard. Also, a third (optional) column can be present, with the sequence of the oligo.
    + One `.config` file with the database details.
- Database query now split in two scripts (`fprode_dbquery_probe` and `fprode_dbquery_probeSet`), for single-probe and probe-set design.
    + Query-related methods moved to the `query` sub-module.
    + Query ID now handled server-side, for easier standalone script execution.
    + Region of interest now passed as `chrN:XXX,YYY`, for convenience.
    + Query name and description now handled only server-side, i.e., removed as input parameters of the query scripts.

### Removed
- `fprode_dbextract`



## [1.1.0] - 2018-08-25
### Changed
- Refactored as Python package.



## [0.0.1] - 2017-08-06 - First release



[1.1.0] https://github.com/ggirelli/fish-prode/releases/tag/v1.1.0  
[0.0.1] https://github.com/ggirelli/fish-prode/releases/tag/v0.0.1  
