% include(vpath + 'header.tpl')

<div id="main" class="col col-md-6 offset-md-3 col-sm-12">

	% if not query['done']:
	% include(vpath + 'query_undone.tpl')
	% else:
	% include(vpath + 'query_done.tpl')
	% end

</div>


% include(vpath + 'footer.tpl')