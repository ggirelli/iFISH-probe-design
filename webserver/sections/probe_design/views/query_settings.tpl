<table class="table">
	<tbody>
		<tr>
			<th>ID</th>
			<td>{{query['query_id']}}</td>
		</tr>
		% if not query['nodata']:
		% keys = ['name', 'description', 'force_mode', 'chrom', 'start', 'end', 'n_probes', 'n_oligo', 'k', 'min_d', 'dbpath', 'max_probes', 'f1_thr', 'win_shift', 'f1', 'f2', 'f3']
		% for k in keys:
		<tr>
			<th>{{k}}</th>
			% if k in ['description', 'dbpath']:
			<td class="break-all">
			% else:
			<td>
			% end
			{{query['data'][k]}}</td>
		</tr>
		% end
		% end
	</tbody>
</table>