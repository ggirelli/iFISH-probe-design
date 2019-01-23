% include(vpath + 'header.tpl')

<div id="main" class="col-xl-6 offset-xl-3 col-12">

	<h1 id="title">
		<a href="{{app_uri}}/q/{{query['data']['query_id']}}" data-toggle="tooltip" data-placement="left" title="Query {{query['data']['query_id']}}"><span class="fa fa-backward"></span></a> 
		Query: {{query['data']['query_id']}} <br />
		<small>Candidate: {{int(candidate['id']) + 1}}</small>
	</h1>

	<div id="description">
		<!-- Silence is golden -->
	</div>

	<div class="container-fluid p-0"><div class="card mb-3">
		<div class="card-block">
			<table>
				<thead></thead>
				<tbody>
					<tr>
						<td colspan="3">
							<img class="img-fluid" src="{{app_uri}}q/{{query['data']['query_id']}}/cs/{{candidate['id']}}/images/windows.png" alt="Candidate #{{candidate['id']}}, probe" />
						</td>
					</tr>
					<tr>
						<td>
							<img class="img-fluid" src="{{app_uri}}q/{{query['data']['query_id']}}/cs/{{candidate['id']}}/images/distr.png" alt="Candidate #{{candidate['id']}}, oligo" />
						</td>
						<td>
							<img class="img-fluid" src="{{app_uri}}q/{{query['data']['query_id']}}/cs/{{candidate['id']}}/images/distance.png" alt="Candidate #{{candidate['id']}}, distance" />
						</td>
					</tr>
				</tbody>
			</table>
		</div>
	</div></div>

	<div class="row">

		<div class="col col-xl-6 col-12">
			<div class="card card-primary card-inverse">
				<div class="card-block">
					<h3 class="card-title">Candidate settings</h3>
					
					<table class="table">
						<tbody>
							<tr>
								<th>id</th>
								<td>{{query['candidates'][int(candidate['id'])][0]}}</td>
							</tr>
							<tr>
								<th>chr</th>
								<td>{{query['candidates'][int(candidate['id'])][1]}}</td>
							</tr>
							<tr>
								<th>start</th>
								<td>{{query['candidates'][int(candidate['id'])][2]}}</td>
							</tr>
							<tr>
								<th>stop</th>
								<td>{{query['candidates'][int(candidate['id'])][3]}}</td>
							</tr>
							<tr>
								<th>n_probes</th>
								<td>{{query['candidates'][int(candidate['id'])][4]}}</td>
							</tr>
							<tr>
								<th>spread</th>
								<td>{{query['candidates'][int(candidate['id'])][5]}}</td>
							</tr>
						</tbody>
					</table>

				</div>
			</div>
		</div>

		<div class="col col-xl-6 col-12"><div class="card mb-3">

			<!-- Nav tabs -->
			<div class="card-header card-outline-primary">
				<ul class="nav nav-tabs card-header-tabs" role="tablist">
					<li role="presentation" class="nav-item">
						<a class="nav-link active" href="#fastaset" aria-controls="fastaset" role="tab" data-toggle="tab">Fasta</a>
					</li>
					<li role="presentation" class="nav-item">
						<a class="nav-link" href="#bedset" aria-controls="bedset" role="tab" data-toggle="tab">Bed</a>
					</li>

					<li role="presentation" class="nav-item ml-auto">
						<a class="nav-link" id="download_set_btn" href="{{app_uri + 'q/' + query['data']['query_id'] + '/cs/' + candidate['id'] + '/documents/set_' + candidate['id'] + '.fa/download/'}}" data-toggle="tooltip" data-placement="top" title="Download fasta"><span class='fa fa-download'></span></a>
					</li>
					<li role="presentation" class="nav-item">
						<a class="nav-link" href="https://genome.ucsc.edu/cgi-bin/hgBlat?command=start" target="_new" data-toggle="tooltip" data-placement="top" title="BLAT"><span class="fa fa-eye"></span></a>
					</li>
				</ul>
			</div>

			<!-- Tab panes -->
			<div class="tab-content card-block">

				<!-- Fasta tab -->
				<div role="tabpanel" class="tab-pane active" id="fastaset">

					<pre class="ws_wrap" style="height: 25em;"><code>
					% import os
					% fapath = vpath + '../query/' + query['data']['query_id']
					% fapath += '/candidates/set_' + candidate['id']
					% fapath += '/set_' + candidate['id'] + '.fa'
					% if os.path.exists(fapath):
					% include(fapath)
					% else:
					No fasta file found...
					% end
					</code></pre>

				</div>

				<!-- Bed tab -->
				<div role="tabpanel" class="tab-pane" id="bedset">

					<pre class="ws_wrap" style="height: 25em;"><code>
					% fapath = vpath + '../query/' + query['data']['query_id']
					% fapath += '/candidates/set_' + candidate['id']
					% fapath += '/set_' + candidate['id'] + '.bed'
					% if os.path.exists(fapath):
					% include(fapath)
					% else:
					No bed file found...
					% end
					</code></pre>

				</div>

			</div>

		</div></div>
	</div>

</div>

<script type="text/javascript">
$(function () {

	// Enable tooltips
	$('[data-toggle="tooltip"]').tooltip()

	// Switch download button
	$('a[aria-controls=fastaset]').click(
		function(e) {
			$('#download_set_btn').attr('href', "{{app_uri + 'q/' + query['data']['query_id'] + '/cs/' + candidate['id'] + '/documents/set_' + candidate['id'] + '.fa/download/'}}");
			$('#download_set_btn').attr('data-original-title', 'Download fasta');
		}
	);
	$('a[aria-controls=bedset]').click(
		function(e) {
			$('#download_set_btn').attr('href', "{{app_uri + 'q/' + query['data']['query_id'] + '/cs/' + candidate['id'] + '/documents/set_' + candidate['id'] + '.bed/download/'}}");
			$('#download_set_btn').attr('data-original-title', 'Download bed');
		}
	);

})
</script>

% include(vpath + 'footer.tpl')