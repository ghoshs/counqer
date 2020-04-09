import math
import pandas as pd
import pprint
import cardinal_processor.myw2n as myw2n
from nltk.corpus import wordnet as wn

"""
function to return a dataframe for caculating median scores
"""
def get_dataframe(valdict):
	df = pd.DataFrame.from_dict(valdict)
	df['integers'] = df['integers'].astype(int)
	df.sort_values('integers', inplace=True)
	df['cumsum'] = df.weight.cumsum()
	return df
""" 
function which takes a list containing snippet tags [{'text':, 'ents':, 'has_ent_match':, 'ent_similarity':, 'integers':}]
and returns median stats on the integers.
"""
def get_cardinal_stats(result):
	# pprint.pprint(result)
	cardinals = {}
	val_dict = {'integers': [], 'pos': [], 'weight': []}
	headn_val_dict = {'integers': [], 'pos': [], 'weight': [], 'sim': [], 'text': [], 'root': [], 'amod': []}
	# for each snippet
	for idx, item in enumerate(result):
		# create a list of integers in the snippet
		val = [x for x in item['integers'] if len(x) > 0]
		# append int list of current snippet to final list of integers with their position
		val_dict['integers'] = val_dict['integers'] + val
		val_dict['pos'] = val_dict['pos'] + [idx+1 for _ in range(0, len(val))]

		# create a list of integers in the snippet with matching headnouns
		val = [x['val'] for x in item['headn_match'] if len(x['val']) > 0]
		# append int list of current snippet to final list of integers with their position, head noun text and similarity
		headn_val_dict['integers'] += val
		headn_val_dict['pos'] += [idx+1 for _ in range(0, len(val))]
		headn_val_dict['sim'] += [x['sim'] for x in item['headn_match'] if len(x['val']) > 0]
		headn_val_dict['text'] += [x['text'] for x in item['headn_match'] if len(x['val']) > 0] 
		headn_val_dict['root'] += [x['root'] for x in item['headn_match'] if len(x['val']) > 0] 
		headn_val_dict['amod'] += [x['amod'] for x in item['headn_match'] if len(x['val']) > 0]

	val_dict['weight'] = [1.0/x for x in val_dict['pos']]
	headn_val_dict['weight'] = [1.0/x for x in headn_val_dict['pos']]

	# do not consider all intgers
	# if len(val_dict['integers']) == 0:
	cardinals['median'] = cardinals['pos_wgt_median'] = ''
	# else:
		# df = get_dataframe(val_dict)
		
		# cutoff = df.weight.sum()/2.0
		# cardinals['integers'] = [{'int': x, 'pos': val_dict['pos'][idx]} for idx, x in enumerate(val_dict['integers'])]
		# cardinals['pos_wgt_median'] = str(df.integers[df['cumsum'] >= cutoff].iloc[0]) if len(df.integers[df['cumsum'] >= cutoff]) > 0 else ''
		# cardinals['median'] = str(math.floor(df.integers.median()))

	if len(headn_val_dict['integers']) == 0:
		cardinals['median_headn'] = cardinals['pos_wgt_median_headn'] = ''
	else:
		df = get_dataframe(headn_val_dict)

		cutoff = df.weight.sum()/2.0
		cardinals['integers_headn'] = [{'int': x, 'pos': headn_val_dict['pos'][idx]} for idx, x in enumerate(headn_val_dict['integers'])]
		cardinals['pos_wgt_median_headn'] = str(df.integers[df['cumsum'] >= cutoff].iloc[0]) if len(df.integers[df['cumsum'] >= cutoff]) > 0 else ''
		cardinals['median_headn'] = str(math.floor(df.integers.median()))
		cardinals['sim_headn'] = headn_val_dict['sim']
		cardinals['text_headn'] = headn_val_dict['text']
		cardinals['root_headn'] = headn_val_dict['root']
		cardinals['amod_headn'] = headn_val_dict['amod']

	return cardinals

"""
function to return list of cardinals from text in integer form 
"""
def get_word_to_num(text_cardinals):
	multiplier = {'hundred', 'thousand', 'million', 'billion', 'trillion', 'lac', 'lakh'}
	integers = []
	for item in text_cardinals:
		try:
			myw2n.word_to_num(item['text'])
		except ValueError:
			val = ''
		else:
			val = str(myw2n.word_to_num(item['text']))
			integers.append(val)
	if len(integers) == 0:
		integers = ['']
	return integers

"""
function to obtain the maximum path similarity between the synsets of snippet head noun and the query head noun 
"""
def max_similarity(chunk, query):
	anomaly=['number']
	chunk_synsets = wn.synsets(chunk.root.text)
	# noun chunks containing named-entities will return empty lists
	# remove noun heads equal to "number"
	query_synsets = [wn.synsets(x.root.text) for x in query.noun_chunks if x.root.text not in anomaly]
	# flatten the list
	query_synsets = [x for sublist in query_synsets for x in sublist]
	print(chunk, chunk.root.text, [x.root.text for x in query.noun_chunks])
	print([wn.path_similarity(d,q) for d in chunk_synsets for q in query_synsets])
	similarity = [wn.path_similarity(d,q) for d in chunk_synsets for q in query_synsets if wn.path_similarity(d,q) is not None]
	max_similarity = max(similarity) if len(similarity) > 0 else 0 
	return max_similarity

"""
function to return integers and their corresponding noun phrases for matched predicates
"""
def get_nummodifiers(doc, query=None):
	cardinal_list = []
	text_nounphrase = []
	similarity_threshold = 0.9
	# get list of cardinal texts
	text_cardinals = [{'text': ent.text, 'id': idx} for idx, ent in enumerate(doc.ents) if ent.label_ == 'CARDINAL']
	# filter noun phrases
	for chunk in doc.noun_chunks:
		# check for cardinals
		if any(a['text'] in chunk.text for a in text_cardinals):
			if query is not None:
				# keep noun phrase with matching phraseword
				if len(chunk.root.text) > 0:
					# match only with noun phrases, not entities
					## call wordnet path similarity function
					sim = max_similarity(chunk, query)
					## SpaCy similarity function  
					# sim = max([x.root.similarity(chunk.root) for x in query.noun_chunks if x not in query.ents])
					# print(chunk.root, [x.root.text for x in query.noun_chunks])
				else:
					sim = 0
				if sim >= similarity_threshold:
					modifier = []
					for token in chunk:
						if token.dep_ == 'amod':
							modifier.append(token.text)
					cardinal_list.append({'val': get_word_to_num([{'text': chunk.text}])[0], 'text': chunk.text, 'root': chunk.root.text, 'sim': str(sim), 'amod': ','.join(modifier)})
	# text_nounphrase = [item for item in text_nounphrase if any(a['text'] in item['text'] for a in text_cardinals)]
	
	# cardinal_list = [{'val': get_word_to_num([item]), 'text': item['text']} for item in text_nounphrase]
	return cardinal_list