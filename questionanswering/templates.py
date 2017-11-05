from string import Template

templates = {
'simple': '''
			select distinct ?result
			where {{
					<http://dbpedia.org/resource/{res}> dbo:{prop} ?result

			}}
			''',
'simple_amb' : '''
					select distinct ?result
					where {{
							<http://dbpedia.org/resource/{res}> dbo:wikiPageDisambiguates ?resource.
							?resource dbo:{prop} ?result
					}}
					'''
				,
'simple_rev': '''
				select distinct ?result
				where {{

				<http://dbpedia.org/resource/{res}> dbo:wikiPageDisambiguates* ?resource.
				?result dbo:{prop} ?resource

				}}
				'''

}