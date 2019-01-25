
<form id="multi_probe_form" action="{{app_uri}}single_queries" method="post" enctype="multipart/form-data">

	<div class="card-body">

		<div class="description">
			<h3 class="card-title">Settings</h3>
			<p>
				If you want to submit multiple single-probe queries at once, please <u>upload and submit</u> a <b>tabulation-separated spreadsheet</b> (.tsv).
				The required columns (and allowed values) in the spreadsheet are the following:
			</p>

			<ul>
				<li><b>name</b></li>
				<li><b>description</b></li>
				<li>
					<b>database</b>
					<ul>
						<li>kmer40_dtm10_gcmin35_gcmax80_hpolyes</li>
					</ul>
				</li>
				<li><b>chromosome</b>: chr1-chr22, chrX, chrY</li>
				<li><b>start position</b>: &ge;0</li>
				<li><b>end position</b>: depends on the chromosome</li>
				<li><b>number of oligomers</b>: &ge; 1</li>
				<li><b>f1_thr</b>: threshold around best feature 1 value, between 0 and 1</li>
				<li><b>max output probes</b>: -1 for all, otherwise &gt;0</li>
				<li><b>feature order</b>: comma-separated values "size", "spread" and "centrality"</li>
			</ul>

			<br />

			<div class="form-group">
				<label for="data">File input:</label>
				<input type="file" name="data" id="data" class="form-control-file" />
				<small class="form-text text-muted">
					Please, see the following <a href="{{app_uri}}documents/example.tsv/mimetype/text/plain" target="_new">example file</a> for clarifications.
					The file should have no header.
				</small>
			</div>
		</div>

		<input type="submit" class="btn btn-success float-right" />
	</div>


</form>
