from nltk.corpus import wordnet as wn
import json
import re
from SPARQLWrapper import SPARQLWrapper, JSON
try: 
	import urllib2 as myurllib
except ImportError:
	import urllib.request as myurllib


# ## server edits ##
# http_proxy = 'http://dmz-gw.mpi-klsb.mpg.de:3128'
# https_proxy = 'https://dmz-gw.mpi-klsb.mpg.de:3128'
# myurllib.install_opener(myurllib.build_opener(myurllib.ProxyHandler({'http': http_proxy, 'https': https_proxy})))

ner_tags = {'person': ['person', 'character'], 'norp': ['nationality', 'religion', 'politics'],
			'fac': ['building', 'airport', 'highway'],
			'org': ['oraganization', 'institution'],
			'gpe': ['country', 'city', 'state'],
			'loc': ['geographical location'],
			'product': ['product'],
			'event': ['event'],
			'work_of_art': ['work', 'book', 'song', 'movie'],
			'law': ['law'],
			'language': ['language']}

ner_synsets = {label: [wn.synsets(item) for item in classes] for (label, classes) in ner_tags.items()}

webisa_conf_threshold = 0.1

def from_nltk_wordnets(json_doc, query):
	## only use the first nounchunk which is not a named-entity
	query = [x.root.text for x in query.noun_chunks if x not in query.ents][0]
	for ent in json_doc['ents']:
		ent_label = ent['label'].lower()
		# if entity label not in ner_tags continue
		if ent_label not in ner_tags:
			continue
		# assign a default noun phrase similarity
		ent['np_sim'] = 0
		# for all tags relevant to the entity
		for tag_synsets in ner_synsets[ent_label]:
			# for every query term, find the max similarity between synsets of an element of the tag label
			# for term in query:
			q_synsets = wn.synsets(query)
			path_similarity = [i.path_similarity(j) for i in q_synsets for j in tag_synsets if i.path_similarity(j) is not None]
			path_similarity = max(path_similarity) if len(path_similarity) > 0 else 0
			if path_similarity > ent['np_sim']:
				ent['np_sim'] = path_similarity
	return json_doc

def call_query(sparql, query):
	results = {'head': {'vars': ['hyponymLabel', 'confidence'], 'link': []}, 'results': {'distinct': False, 'bindings': [], 'ordered': True}}
	sparql.setQuery(query)
	try:
		results = sparql.query().convert()
	except Exception as e:
		print('Sparql endpoint query error:\n%s \nOn query:\n%s'%(e, query))
	finally:
		return results

def webisa_to_dict(results):
	broaderDict = {}
	for item in results['results']['bindings']:
		if float(item['confidence']['value']) < webisa_conf_threshold:
			break
		broaderDict[item['hyponymLabel']['value']] = item['confidence']['value']
	return broaderDict

def webisadb_sparql(sparql, entity):
	sparql.setReturnFormat(JSON)
	## server edits
	# sparql.addParameter('http', http_proxy)
	# sparql.addParameter('https', https_proxy)
	prefix = '''PREFIX isa: <http://webisa.webdatacommons.org/concept/>
						PREFIX isaont: <http://webisa.webdatacommons.org/ontology#> 
						SELECT ?hyponymLabel ?confidence
						WHERE{GRAPH ?g 
						{isa:'''
	suffix = ''' skos:broader ?hyponym.}
						?hyponym rdfs:label ?hyponymLabel.
						?g isaont:hasConfidence ?confidence.
						}
						ORDER BY DESC(?confidence)'''
	# query with underscores on both ends _entity_
	results = call_query(sparql, prefix+'_'+entity+'_'+suffix)
	# in case of empty results, query with underscore in the end only
	if len(results['results']['bindings']) == 0:
		results = call_query(sparql, prefix+entity+'_'+suffix)
		# in case of empty results, query with underscore in place of full stops
		new_entity = entity.replace('.', '_')
		new_entity = new_entity.replace('__', '_')
		if len(results['results']['bindings']) == 0:
			results = call_query(sparql, prefix+'_'+new_entity+'_'+suffix)
			if len(results['results']['bindings']) == 0:
				results = call_query(sparql, prefix+new_entity+'_'+suffix)

	return webisa_to_dict(results) 


def from_webIsaDB(json_doc, query):
	sparql = SPARQLWrapper("http://webisa.webdatacommons.org/sparql", agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")    
	## use the first noun chunk which is not a named-entity
	query_nouns = [x.root.text for x in query.noun_chunks if x not in query.ents][0]
	q_broaderDict = webisadb_sparql(sparql, query_nouns)

	for ent in json_doc['ents']:
		if ent['label'].lower() not in ner_tags:
			continue
		entity = json_doc['text'][ent['start']:ent['end']]
		if ',' in entity:
			continue
		entity = '_'.join(entity.split(' '))
		entity = entity.lower()
		# remove possesive form
		entity = entity.replace("'s", '')
		ent_broaderDict = webisadb_sparql(sparql, entity)
		ent['np_sim'] = 0
		# check if query noun text directly present in broaderDict
		if query_nouns in ent_broaderDict:
			ent['np_sim'] = 1.0
		# check if hyponym set of query noun intersects with entity hyponym
		else:
			if any([item in q_broaderDict for item in ent_broaderDict]):
				ent['np_sim'] = 1.0
		# print(query_nouns, ",", entity, ent['np_sim'])
	return json_doc
	

def get_enumerations(json_doc, query):
	# snippet = json_doc['text'] 
	# tag_similarity = {}

	### using wordnet synsets
	# json_doc = from_nltk_wordnets(json_doc, query)
	
	### using webIsaDB LOD
	json_doc = from_webIsaDB(json_doc, query)

	return json_doc