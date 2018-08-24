Single queries
==============

By uploading a **spreadsheet** with one single probe query per row, it is possible to simultaneously load multiple queries in the queue. The queued queries will still be executed one at a time, as explained in the ``single query`` section.

The required columns (and allowed values) in the spreadsheet are the following:

* **name**
* **description**
* **database**
	* kmer40_dtm10_gcmin35_gcmax80_hpolyes
* **chromosome**: chr1-chr22, chrX, chrY
* **start position**: ≥0
* **end position**: depends on the chromosome
* **number of oligomers**: ≥ 1
* **feature threshold**: between 0 and 1
* **max output probes**: -1 for all, otherwise >0
* **feature order**: comma-separated values "size", "spread" and "centrality"

Please, see the following `example file </probe-design/documents/example.tsv/mimetype/text/plain>`_ for clarifications. The file should have no header.
