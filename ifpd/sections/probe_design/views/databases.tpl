%import os
<ul class="list-group list-group-flush">
	<li class="list-group-item">
		<h5>Available databases:</h5>
		<ul class="database-list">
			% for (dbName, dbDir) in dblist.items():
			<li>
				<a href="#{{dbName}}">{{dbName}}</a>
			</li>
			%end
		</ul>
	</li>
	<li class="list-group-item">
		<div class="container-fluid row">
			%for config in dbdata:
			<div class="col col-12 col-md-6"><div class="card database-card">
				<div class="card-body">
					<h5 class="card-title"><a id="{{config['DATABASE']['name']}}">
						{{config['DATABASE']['name']}}
					</a></h5>
					<h6 class="card-subtitle mb-2 text-muted">
						<code>{{os.path.basename(config['SOURCE']['outdirectory'])}}</code>
					</h6>
				</div>
				<ul class="list-group list-group-flush">
					<li class="list-group-item">
						<b>Reference genome:</b> {{config['DATABASE']['refgenome']}}
					</li>
					<li class="list-group-item">
						<b>Minimum oligo distance:</b> {{config['OLIGOS']['min_dist']}} nt
					</li>
					<li class="list-group-item">
							<b>Oligo length range:</b> {{config['OLIGOS']['min_length']}}-{{config['OLIGOS']['max_length']}} nt
					</li>
					<li class="list-group-item">
						<b>Overlapping oligos:</b> {{config['OLIGOS']['overlaps']}}
					</li>
					%for k in [k for k in config['CUSTOM'].keys() if not k in ['reference', 'url']]:
					<li class="list-group-item">
						<b>{{k}}:</b> {{config['CUSTOM'][k]}}
					</li>
					%end
				</ul>
				<div class="card-body">
					%if 'reference' in config['CUSTOM'].keys():
					<p class="card-text reference"><b>Reference: </b>{{config['CUSTOM']['reference']}}</p>
					%end
					%if 'url' in config['CUSTOM'].keys():
					<a href="{{config['CUSTOM']['url']}}" target="_new" class="card-link"><i class="fas fa-external-link-alt text-primary"></i> Database link</a>
					%end
				</div>
			</div></div>
			%end
		</div>
	</li>
</ul>