
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