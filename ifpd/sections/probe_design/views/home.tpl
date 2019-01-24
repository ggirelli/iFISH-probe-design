% include(vpath + 'header.tpl')

<!-- header -->
<div class="row">
	<div id="main" class="col col-xl-6 offset-xl-3 col-lg-12">

		<h1 id="title">
			iFISH Probe Designer
		</h1>
		
		%if breadcrumbs:
		<nav aria-label="breadcrumb">
			<ol class="breadcrumb">
				<li class="breadcrumb-item"><a href="/">Home</a></li>
				<li class="breadcrumb-item active" aria-current="page">Design</li>
			</ol>
		</nav>
		%end

		<div id="abstract">
			Here you can <u>design</u> new single probes or spotting probes. Go to the <a href="javascript:$('a[aria-controls=\'new_query\']').click();">Single Probe</a> page to design one probe in a region of interest. Instead, to query for a number of probes in a single region of interest use <a href="javascript:$('a[aria-controls=\'new_multi_query\']').click();">Spotting Probe</a>. More details in the corresponding page.
		</div>

		<div class="row">
			<!-- main panel -->
			<div class="col col-12">
				<div id="designer" class="card">
					<div class="card-header card-outline-primary">

						<!-- Nav tabs -->
						<ul class="nav nav-tabs card-header-tabs">
							<li role="presentation" class="nav-item">
								<a class="nav-link active" href="#new_query" aria-controls="new_query" role="tab" data-toggle="tab">Single probe</a>
							</li>
							<li role="presentation" class="nav-item">
								<a class="nav-link" href="#new_multi_query" aria-controls="new_multi_query" role="tab" data-toggle="tab">Spotting Probe</a>
							</li>
							<li role="presentation" class="nav-item">
								<a class="nav-link" href="#databases" aria-controls="databases" role="tab" data-toggle="tab">Databases</a>
							</li>
							<li rolw="presentation" class="nav-item">
								<a class="nav-link" href="https://ggirelli.github.io/iFISH-probe-design/" target="_new" data-toggle="tooltip" data-placement="top" title="Help">
									<span class="fas fa-info-circle"></span>
								</a>
							</li>
							<li rolw="presentation" class="nav-item">
								<a class="nav-link" href="http://genome.ucsc.edu/cgi-bin/hgTracks" target="_new" data-toggle="tooltip" data-placement="top" title="Genome Browser">
									<span class="fas fa-dna"></span>
								</a>
							</li>
						</ul>

					</div>

					<!-- Tab panes -->
					<div class="card-block">
						<div class="tab-content">

							<div role="tabpanel" class="tab-pane active overflow" id="new_query">
								% include(vpath + 'single_query_form.tpl')
							</div>

							<div role="tabpanel" class="tab-pane overflow" id="new_multi_query">
								% include(vpath + 'multi_query_form.tpl')
							</div>

							<div role="tabpanel" class="tab-pane overflow" id="databases">
								% include(vpath + 'databases.tpl')
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- query search panel -->
			<div id="search" class="col col-12">
				<div class="card">

					<!-- Nav tabs -->
					<div class="card-header border-warning">
						<ul class="nav nav-tabs card-header-tabs" role="tablist">
							<li role="presentation" class="nav-item"><a class="nav-link active" >Search a query</a></li>
						</ul>
					</div>

					<div class="card-body">
						<form action="javascript:document.location='{{app_uri}}q/'+$('#query_id_search')[0].value;">
							<input id="query_id_search" class="form-control" type="text" name="search_query_by_id" placeholder="Insert your query ID and press enter." />
						</form>
					</div>

				</div>
			</div>

			<!-- queue panel -->
			<div id="queue" class="col col-12">
				<div class="card">

					<!-- Nav tabs -->
					<div class="card-header border-success">
						<ul class="nav nav-tabs card-header-tabs" role="tablist">
							<li role="presentation" class="nav-item"><a class="nav-link active" href="#queue" aria-controls="queue" role="tab" data-toggle="tooltip" data-placement="top" title="Here you can find the queries in the queue (i.e., waiting to run).">Queue</a></li>
							<li rolw="presentation" class="nav-item ml-auto">
								<a class="nav-link text-success" href="{{app_uri}}" data-toggle="tooltip" data-placement="top" title="Refresh">
									<span class="fas fa-redo-alt"></span>
								</a>
							</li>
						</ul>
					</div>

					<div class="card-body">
						<p></p>
						<table>
							% if 0 == len(queue.queue):
							<tr>
								<td>The queue is currently empty.</td>
							</tr>
							% end
							% for i in range(len(queue.queue)):
							<tr>
								<td>
									{{i + 1}}: Query #{{queue.queue[i][1]}} - {{queue.queue[i][2]}}
								</td>
							</tr>
							% end
						</table>
					</div>

				</div>
			</div>
		</div>
	</div>
</div>

% include(vpath + 'footer.tpl')
