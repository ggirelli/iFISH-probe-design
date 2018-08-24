% include(vpath + 'header.tpl')


<!-- header -->
<div class="row">
	<div id="header" class="col col-md-6 offset-md-3">

		<h1 id="title">
			<a href="{{root_uri}}" data-toggle="tooltip" data-placement="left" title="home"><span class="fa fa-backward"></span></a> Probe Designer
		</h1>

		<div id="description">
			You can create new probes from the <b>query(-ies)</b> tabs,<br/ >or visualize and download old probes in the <b>index</b> tab.
		</div>

	</div>
</div>

<div class="row">
	<!-- main panel -->
	<div id="main" class="card card-block col col-md-6 offset-md-3 px-0 pt-0 mb-3">

		<div class="card-header card-outline-primary">

			<!-- Nav tabs -->
			<ul class="nav nav-tabs card-header-tabs" role="tablist">
				<li role="presentation" class="nav-item">
					<a class="nav-link active" href="#index" aria-controls="index" role="tab" data-toggle="tab">
						Index
					</a>
				</li>
				<li class="nav-item dropdown">
					<a class="nav-link dropdown-toggle" data-toggle="dropdown" href="#" role="button" aria-haspopup="true" aria-expanded="false">Single probe</a>
					<div class="dropdown-menu">
						<a class="dropdown-item" href="#new_query" aria-controls="new_query" role="tab" data-toggle="tab">Query</a>
						<a class="dropdown-item" href="#new_queries" aria-controls="new_queries" role="tab" data-toggle="tab">Queries</a>
					</div>
				</li>
				<li role="presentation" class="nav-item">
					<a class="nav-link" href="#new_multi_query" aria-controls="new_multi_query" role="tab" data-toggle="tab">
						Multi probe
					</a>
				</li>
				<!-- left tab blocks starts with .ml-auto element -->
				<li rolw="presentation" class="nav-item ml-auto float-right">
					<a class="nav-link" href="/docs/_static/probe_designer.html" target="_new" data-toggle="tooltip" data-placement="top" title="Help">
						<span class="fa fa-info-circle"></span>
					</a>
				</li>
				<li rolw="presentation" class="nav-item float-right">
					<a class="nav-link" href="http://genome.ucsc.edu/cgi-bin/hgTracks" target="_new" data-toggle="tooltip" data-placement="top" title="Genome Browser">
						<span class="fa fa-external-link-square"></span>
					</a>
				</li>
			</ul>

		</div>

		<div class="card-block">

			<!-- Tab panes -->
			<div class="tab-content">

				<!-- Index tab -->
				<div role="tabpanel" class="tab-pane active overflow" id="index">

					% include(vpath + 'index_table.tpl')

				</div>

				<!-- New single query tab -->
				<div role="tabpanel" class="tab-pane overflow" id="new_query">

					% include(vpath + 'single_query_form.tpl')

				</div>

				<!-- New single queries tab -->
				<div role="tabpanel" class="tab-pane overflow" id="new_queries">

					% include(vpath + 'single_queries_form.tpl')

				</div>

				<!-- New single queries tab -->
				<div role="tabpanel" class="tab-pane overflow" id="new_multi_query">

					% include(vpath + 'multi_query_form.tpl')

				</div>
			</div>

		</div>

	</div>

	<!-- queue panel -->
	<div id="queue" class="col col-md-3">
		<div class="card card-block col col-md-8 offset-md-2 px-0 pt-0">

			<div class="card-header card-outline-warning">

				<!-- Nav tabs -->
				<ul class="nav nav-tabs card-header-tabs" role="tablist">
					<li role="presentation" class="nav-item"><a class="nav-link active" href="#queue" aria-controls="queue" role="tab" data-toggle="tab">Queue</a></li>
					<li rolw="presentation" class="nav-item ml-auto">
						<a class="nav-link" href="{{app_uri}}" data-toggle="tooltip" data-placement="top" title="Refresh">
							<span class="fa fa-refresh"></span>
						</a>
					</li>
				</ul>


			</div>

			<div class="card-block">

				% if 0 == len(queue.queue):
				<tr>
					<td>Empty queue...</td>
				</tr>
				% end
				% for i in range(len(queue.queue)):
				<tr>
					<td>
						{{i + 1}}: Query #{{queue.queue[i][1]}} - {{queue.queue[i][2]}}
					</td>
				</tr>
				% end

			</div>

		</div>
	</div>
</div>


% include(vpath + 'footer.tpl')