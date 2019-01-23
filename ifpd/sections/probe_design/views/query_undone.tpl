<h1 id="title">
	<a href="{{app_uri}}" data-toggle="tooltip" data-placement="left" title="Probe designer"><span class="fa fa-backward"></span></a> 
	Query: {{query['query_id']}}
</h1>

<div id="description">
	% doing = [' '.join(q) for q in queue.doing]
	% if query['cmd'] in doing:
	<span class="text-success">Still running...</span>
	% else:
	<span class="text-danger">{{query['error']}}</span>
	% end
</div>

<div class="container-fluid p-0"><div class="card mb-3">

	<div class="card-header card-outline-primary">
		<!-- Nav tabs -->
		<ul class="nav nav-tabs card-header-tabs" role="tablist">
			<li role="presentation" class="nav-item"><a class="nav-link active" href="#table_tab" aria-controls="table_tab" role="tab" data-toggle="tab">Table</a></li>
			<li role="presentation" class="nav-item"><a class="nav-link" href="#comparison_tab" aria-controls="comparison_tab" role="tab" data-toggle="tab">Figures</a></li>
		</ul>
	</div>

	<!-- Tab panes -->
	<div class="tab-content card-block">

		<!-- Table tab -->
		<div role="tabpanel" class="tab-pane active overflow" id="table_tab">

			% if int(query['data']['n_probes']) == 1:
				% if not query['nodata']:
				% include(vpath + 'candidate_probe_table.tpl')
				% else:
				% include(vpath + 'candidate_probe_figures.tpl')
				% end
			% else:
				% if not query['nodata']:
				% include(vpath + 'candidate_probe_set_table.tpl')
				% else:
				% include(vpath + 'candidate_probe_set_figures.tpl')
				% end
			% end

		</div>

		<!-- Comparison tab -->
		<div role="tabpanel" class="tab-pane overflow" id="comparison_tab">

			% if int(query['data']['n_probes']) == 1:
			% include(vpath + 'candidate_probe_figures.tpl')
			% else:
			% include(vpath + 'candidate_probe_set_figures.tpl')
			% end

		</div>

	</div>

</div></div>

<div class="row">
	<div class="col col-xl-6 col-12">
		<div class="card card-primary card-inverse mb-3">
			<div class="card-block">
				<h3 class="card-title">Query settings</h3>
				% include(vpath + 'query_settings.tpl')
			</div>
		</div>
	</div>

	<div class="col col-xl-6 col-12">
		<div class="card card-secondary mb-3">
			<div class="card-block">
				<h3 class="card-title">Cmd</h3>
				<pre class="ws_wrap m-0" style="max-height: 25em;"><code>{{query['cmd']}}</code></pre>
			</div>
		</div>

		<div class="card card-secondary mb-3">
			<div class="card-block">
				<h3 class="card-title">Log</h3>
				<pre class="ws_wrap m-0" style="max-height: 25em;"><code>{{query['log']}}</code></pre>
			</div>
		</div>
	</div>
</div>
