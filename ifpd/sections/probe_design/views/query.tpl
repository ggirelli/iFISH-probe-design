% include(vpath + 'header.tpl')

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
					<a href="{{app_uri}}q/{{query['id']}}">Query: {{query['id']}}</a>
				</li>
			</ol>
		</nav>
		%end

		<div id="abstract">
			<h4>{{query['name']}}</h4>
			<h6 class="isotime">{{query['isotime']}}</h6>
			{{query['description']}}
		</div>

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

		<div class="row">
			<div class="col col-xl-6 col-12">
				<div class="card bg-primary text-white mb-3">
					<div class="card-body">
						<h3 class="card-title">Query settings</h3>
						<ul class="list-group list-group-flush query_settings">
							<li class="list-group-item bg-primary">
								<b>Name:</b> {{query['name']}}
							</li>
							<li class="list-group-item bg-primary">
								<b>Time:</b> {{query['isotime']}}
							</li>
							<li class="list-group-item bg-primary">
								<b>Database:</b> {{query['db']}}
							</li>
							<li class="list-group-item bg-primary">
								<b># oligos per probe:</b> {{query['n_oligo']}}
							</li>
							<li class="list-group-item bg-primary">
								<b>Feature #1 threshold:</b> {{query['threshold']}}
							</li>
							<li class="list-group-item bg-primary">
								<b>Max # output probes:</b> {{query['max_probes']}}
							</li>
							<li class="list-group-item bg-primary">
								<b>Feature order::</b> {{query['f1']}}, {{query['f2']}}, {{query['f3']}}
							</li>
						</ul>
					</div>
				</div>
			</div>

			<div class="col col-xl-6 col-12">
				<div class="card border-secondary mb-3">
					<div class="card-body">
						<h3 class="card-title">Cmd</h3>
						<pre class="ws_wrap m-0" style="max-height: 25em;"><code>{{query['cmd']}}</code></pre>
					</div>
				</div>

				<div class="card border-secondary mb-3">
					<div class="card-body">
						<h3 class="card-title">Log</h3>
						<pre class="ws_wrap m-0" style="max-height: 25em;"><code>log</code></pre>
					</div>
				</div>
			</div>
		</div>

	</div>
</div>

% include(vpath + 'footer.tpl')