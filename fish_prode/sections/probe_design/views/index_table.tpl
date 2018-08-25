
<input id="query_search" type="text" class="form-control" placeholder='Search query by name...' />

<table class="table table-hover text-center">
	<thead class="thead-default">
		<tr>
			<th>ID</th>
			<th>Type</th>
			<th>Name</th>
			<th>Chr</th>
			<th>Start</th>
			<th>End</th>
			<th>k</th>
			<th># Probes</th>
			<th># Oligomers</th>
			<th>Download</th>
		</tr>
	</thead>
	<tbody>
	%
	% # No query found (non run yet)
	% if 0 == len(qlist):
		<tr>
			<td colspan="10">No query found...</td>
		</tr>
	% end
	%
	% # List finished queries
	% for q in [q for q in qlist if q['done']]:
		<tr>
			<td><a href="{{ app_uri + 'q/' + q['query_id'] }}">Query #{{q['query_id']}}</a></td>
			% if int(q['data']['n_probes']) == 1:
			<td>S</td>
			% else:
			<td>M</td>
			% end
			<td class="name_cell">{{q['data']['name']}}</td>
			<td>{{q['data']['chrom']}}</td>
			<td>{{q['data']['start']}}</td>
			<td>{{q['data']['end']}}</td>
			<td>{{q['data']['k']}}</td>
			<td>{{q['data']['n_probes']}}</td>
			<td>{{q['data']['n_oligo']}}</td>
			<td>
				<a href="{{app_uri}}q/{{q['data']['query_id']}}/download/"><span class="fa fa-download"></span></a>
			</td>
		</tr>
	% end
	%
	% # List unfinished queries
	% for q in [q for q in qlist if not q['done']]:
		<tr>
			% if int(q['data']['n_probes']) == 1:
			<td>S</td>
			% else:
			<td>M</td>
			% end
			% doing = [' '.join(q) for q in queue.doing]
			% if any([x in q['cmd'] for x in doing]):
			<td colspan="7" class="text-success">
				Still running...
			</td>
			% else:
			<td colspan='7' class="text-danger">
				% if 0 != len(q['error']):
				{{q['error']}}
				% else:
				Query interrupted for unknown reasons. Contact the system administrator.
				% end
			</td>
			% end
		</tr>
	%end

	<!-- nothing found from searching -->
	<tr>
		<td id="no_found" colspan="10">No query found...</td>
	</tr>
	</tbody>
</table>

<script type="text/javascript">
	
$("#no_found").hide()
$("#query_search").change(
	function(e) {

		// Halt behavior if no queries are available
		if ( 0 == $(".name_cell").length ) {
			return;
		}

		// Retreive search string
		var search_string = $(this).val().toLowerCase();

		// Found queries counter
		var c = 0;

		// Select queries
		$(".name_cell").each(
			function() {
				// Get query row name
				name = $(this).text().toLowerCase();

				// Compare query name and search string
				if ( name.indexOf(search_string) >= 0 ) {

					// Show query
					$(this).parent().show();
					c++;

				} else {

					// Hide query
					$(this).parent().hide();

				}
			}
		);

		// Show no query found message
		if ( 0 == c ) { $("#no_found").show(); }
		else { $("#no_found").hide(); }

	}
);

</script>