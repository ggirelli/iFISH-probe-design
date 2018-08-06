<table class="table table-hover">
	<thead></thead>
	<tbody>
		% cs = query['candidates']
		% if 0 == len(cs):
		<tr>
			<td colspan="3" class="tac">No candidate found...</td>
		</tr>
		% end
		% for ci in range(len(query['candidates'])):
		<tr>
			<td>
				<a href="{{app_uri}}q/{{query['data']['query_id']}}/c/{{ci}}" style="">
					#{{ci + 1}}
				</a>
			</td>
			<td>
				<img class="img-fluid" src="{{app_uri}}q/{{query['data']['query_id']}}/c/{{ci}}/images/window.png" alt="Candidate #{{ci}}, window" />
			</td>
			<td>
				<img class="img-fluid" src="{{app_uri}}q/{{query['data']['query_id']}}/c/{{ci}}/images/distance.png" alt="Candidate #{{ci}}, distance distribution" />
			</td>
		</tr>
		% end
		
	</tbody>
</table>
