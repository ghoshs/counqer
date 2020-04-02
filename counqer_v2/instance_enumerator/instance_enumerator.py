from nltk.corpus import wordnet as wn

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

def get_enumerations(json_doc, query):
	snippet = json_doc['text'] 
	query = [x.root.text for x in query.noun_chunks][0]
	tag_similarity = {}
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