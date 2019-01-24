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
				<li class="breadcrumb-item"><a href="{{app_uri}}q/{{query['id']}}">Query: {{query['id']}}</a></li>
				<li class="breacrumb-item" aria-current="page">Candidate: {{candidate['id']}}</li>
			</ol>
		</nav>
		%end
		
		<div class="container-fluid p-0"><div class="card mb-3">
			<div class="card-header">Candidate plots</div>
			<div class="card-body">
				<table>
					<tbody>
						<tr>
							<td colspan="3">
								<img class="img-fluid" src="{{app_uri}}q/{{query['id']}}/c/{{candidate['id']}}/images/probe.png" alt="Candidate #{{candidate['id']}}, probe" />
							</td>
						</tr>
						<tr>
							<td>
								<img class="img-fluid" src="{{app_uri}}q/{{query['id']}}/c/{{candidate['id']}}/images/window.png" alt="Candidate #{{candidate['id']}}, window" />
							</td>
							<td>
								<img class="img-fluid" src="{{app_uri}}q/{{query['id']}}/c/{{candidate['id']}}/images/oligo.png" alt="Candidate #{{candidate['id']}}, oligo" />
							</td>
							<td>
								<img class="img-fluid" src="{{app_uri}}q/{{query['id']}}/c/{{candidate['id']}}/images/distance.png" alt="Candidate #{{candidate['id']}}, distance" />
							</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div></div>
	
	</div>
</div>

% include(vpath + 'footer.tpl')