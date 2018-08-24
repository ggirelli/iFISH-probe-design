<table class="table table-hover text-center">
	<thead class="thead-default">
		<th>ID</th>
		<th>Chr</th>
		<th>Start</th>
		<th>End</th>
		<th># Probes</th>
		<th>Spread</th>
		<th class="tac">Download</th>
	</thead>
	% cs = query['candidates']
	% if 0 == len(cs):
	<tr>
		<td colspan="9" class="tac">No candidate found...</td>
	</tr>
	% end
	% for ci in range(len(cs)):
	<tr>
		% for di in range(len(cs[ci])):
		% if 0 == di:
		<td>
			<a href="{{app_uri}}q/{{query['data']['query_id']}}/cs/{{cs[ci][di]}}">
				Candidate #{{cs[ci][di] + 1}}
			</a>
		</td>
		% elif 1 != di:
		<td>{{round(cs[ci][di], 6)}}</td>
		% else:
		<td>{{cs[ci][di]}}</td>
		% end
		% end
		<td class="tac">
			<a href="{{app_uri}}q/{{query['data']['query_id']}}/cs/{{ci}}/download/"><span class="fa fa-download"></span></a>
		</td>
	</tr>
	% end
</table>
