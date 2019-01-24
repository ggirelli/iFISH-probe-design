%import os
%import time
%include(vpath + 'header.tpl')

<!-- header -->
<div class="row">
	<div id="main" class="col col-xl-6 offset-xl-3 col-lg-12">

		<h1 id="title">
			Query
		</h1>
		
		%if breadcrumbs:
		<nav aria-label="breadcrumb">
			<ol class="breadcrumb">
				<li class="breadcrumb-item"><a href="/">Home</a></li>
				<li class="breadcrumb-item"><a href="/probe-design/">Design</a></li>
				<li class="breadcrumb-item break-all" aria-current="page">
					<a href="{{app_uri}}q/{{query['id']}}" data-toggle="tooltip" data-placement="bottom" title="Right click on this link, and save it as a bookmark to re-visit it later.">Query: {{query['id']}}</a>
				</li>
			</ol>
		</nav>
		%end

		%if not 'hidden_bookmark_alter' in query.keys():
		<div class="alert alert-dark" role="alert">
			<b>Save the link to this page to be able get back here!</b><a class="float-right text-dark text-decoration-none" href="javascript:alert('Need to add AJAX request to hide this alert.');"><i class="fas fa-times"></i></a>
		</div>
		%end

		%if query['status'] == 'queued':
		%if time.time() - float(query['time']) > queryTimeout:
			<div class="alert alert-danger" role="alert">
				This query timed out (queried@{{query['isotime']}}). Please, try again or contact the <a href="mailto:{{admin_email}}">server admin</a>.
			</div>
		%else:
			<div class="alert alert-warning" role="alert">
				<a class="text-warning" href="{{app_uri}}q/{{query['id']}}" data-toggle="tooltip" data-placement="top" title="Refresh"><span class="fas fa-redo-alt"></span></a>&nbsp;
				This query was queued at {{query['isotime']}}.
			</div>
		%end
		%end
		%if query['status'] == 'running':
		%if time.time() - float(query['start_time']) > queryTimeout:
			<div class="alert alert-danger" role="alert">
				This query timed out (started@{{query['start_isotime']}}). Please, try again or contact the <a href="mailto:{{admin_email}}">server admin</a>.
			</div>
		%else:
			<div class="alert alert-warning" role="alert">
				<a class="text-warning" href="{{app_uri}}q/{{query['id']}}" data-toggle="tooltip" data-placement="top" title="Refresh"><span class="fas fa-redo-alt"></span></a>&nbsp;
				This query has been running since {{query['start_isotime']}} ({{"%.3f" % (time.time() - float(query['start_time']))}} seconds), after being queued for {{"%.3f" % (float(query['start_time']) - float(query['time']))}} seconds. {{queryTimeout}}
			</div>
		%end
		%end
		%if query['status'] == 'done':
			<div class="alert alert-success" role="alert">
				This query was completed at {{query['done_isotime']}}, after running for {{"%.3f" % (float(query['done_time']) - float(query['start_time']))}} seconds.
			</div>
		%end

		<div id="abstract">
			<h4>{{query['name']}}</h4>
			<h6 class="isotime">{{query['isotime']}}</h6>
			{{query['description']}}
		</div>

		%if query['status'] == 'done':
		<div class="container-fluid p-0"><div class="card mb-3">
			<div class="card-header border-primary">
				<!-- Nav tabs -->
				<ul class="nav nav-tabs card-header-tabs" role="tablist">
					<li role="presentation" class="nav-item"><a class="nav-link active" href="#table_tab" aria-controls="table_tab" role="tab" data-toggle="tab">Table</a></li>
					<li role="presentation" class="nav-item"><a class="nav-link" href="#comparison_tab" aria-controls="comparison_tab" role="tab" data-toggle="tab">Figures</a></li>
				</ul>
			</div>

			<div class="tab-content card-body">
				<div role="tabpanel" class="tab-pane active overflow" id="table_tab">
					Data. Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
					tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
					quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
					consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
					cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
					proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
				</div>

				<div role="tabpanel" class="tab-pane overflow" id="comparison_tab">
					Figures. Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
					tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
					quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
					consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
					cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
					proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
				</div>
			</div>
		</div></div>
		%end

		<div class="row">
			<div class="col col-xl-6 col-12">
				<div class="card border-primary mb-3">
					<div class="card-body">
						<h3 class="card-title">Query settings</h3>
						<ul class="list-group list-group-flush query_settings">
							<li class="list-group-item border-primary">
								<b>Name:</b> {{query['name']}}
							</li>
							<li class="list-group-item border-primary">
								<b>Time:</b> {{query['isotime']}}
							</li>
							<li class="list-group-item border-primary">
								<b>Type:</b> {{query['type']}}
							</li>
							<li class="list-group-item border-primary">
								<b>Database:</b> {{query['db']}}
							</li>
							<li class="list-group-item border-primary">
								<b># oligos per probe:</b> {{query['n_oligo']}}
							</li>
							<li class="list-group-item border-primary">
								<b>Feature #1 threshold:</b> {{query['threshold']}}
							</li>
							%if query['type'] == "single":
							<li class="list-group-item border-primary">
								<b>Max # output probes:</b> {{query['max_probes']}}
							</li>
							%else:
							<li class="list-group-item border-primary">
								<b># of probes:</b> {{query['n_probes']}}
							</li>
							<li class="list-group-item border-primary">
								<b>Windows shift:</b> {{query['window_shift']}}
							</li>
							%end
							<li class="list-group-item border-primary">
								<b>Feature order:</b> {{query['f1']}}, {{query['f2']}}, {{query['f3']}}
							</li>
						</ul>
					</div>
				</div>
			</div>

			<div class="col col-xl-6 col-12">
				<div class="card border-secondary mb-3">
					<div class="card-body">
						<h3 class="card-title">Cmd</h3>
						<pre class="ws_wrap m-0" style="max-height: 25em;">{{query['cmd']}}</pre>
					</div>
				</div>
			</div>

			<div class="col col-12">
				<div class="card border-secondary mb-3">
					<div class="card-body">
						<h3 class="card-title">Log</h3>
						%if os.path.isdir(os.path.join(queryRoot, query['id'])):
						%with open(os.path.join(queryRoot, query['id'], 'log')) as IH:
						<pre class="m-0" style="max-height: 25em;">{{"".join(IH.readlines())}}</pre>
						%end
						%else:
						<pre class="ws_wrap m-0" style="max-height: 25em;">Log not found.</pre>
						%end
					</div>
				</div>
			</div>
		</div>

	</div>
</div>

% include(vpath + 'footer.tpl')