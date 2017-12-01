from string import Template

templates = {
'simple': '''
			select distinct ?result
			where {{
					<http://dbpedia.org/resource/{res}> dbo:{prop} ?result

			}}
			''',
'simple_amb' : '''
					select distinct ?result ?resource
					where {{
							<http://dbpedia.org/resource/{res}> dbo:wikiPageDisambiguates ?resource.
							?resource dbo:{prop} ?result .
							
					}}
					'''
				,
'get_abstract' : '''
	select distinct ?result
	where {{
			<{res}> dbo:abstract ?result.
		    FILTER (lang(?result) = 'es')			
	}}
	'''
				,
'simple_rev': '''
				select distinct ?result
				where {{

				<http://dbpedia.org/resource/{res}> dbo:wikiPageDisambiguates* ?resource.
				?result dbo:{prop} ?resource

				}}
				''',
'props_ent': '''
		SELECT distinct ?p WHERE {{
			<http://dbpedia.org/resource/{ent}> ?p ?v.

		}}
		''',
'props_ent_amb': 
		'''
		SELECT distinct ?p WHERE {{
			<http://dbpedia.org/resource/{ent}> dbo:wikiPageDisambiguates* ?uri.
			?uri ?p ?v.
		}}
		''',
'props_ent_rev': '''
		SELECT distinct ?p WHERE {{
			?p ?v <http://dbpedia.org/resource/{ent}>.

		}}''',
'props_type':'''
		SELECT distinct ?p WHERE {{
			?instance a <http://dbpedia.org/ontology/{ent}> . 
         	?instance ?p ?obj .
		}}
		'''
		
		

}