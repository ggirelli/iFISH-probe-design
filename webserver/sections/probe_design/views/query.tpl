% include(vpath + 'header.tpl')

<div id="main" class="col col-md-6 offset-md-3 col-sm-12">

	<div class="row">
		<div class="col col-3">
			<a href="https://bienkocrosettolabs.org/research-in-the-bienko-lab/" target="_new">
				<img class="img-fluid" src="{{root_uri}}images/bienko_lab_logo.png" alt="bienko-lab-logo" />
			</a>
		</div>
		<div class="col col-3 offset-6">
			<a href="https://bienkocrosettolabs.org/research-in-the-crosetto-lab/" target="_new">
				<img class="img-fluid" src="{{root_uri}}images/crosetto_lab_logo.png" alt="crosetto-lab-logo" />
			</a>
		</div>
	</div>

	% if not query['done']:
	% include(vpath + 'query_undone.tpl')
	% else:
	% include(vpath + 'query_done.tpl')
	% end

</div>


% include(vpath + 'footer.tpl')