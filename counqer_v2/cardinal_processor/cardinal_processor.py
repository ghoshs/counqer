import math
import pandas as pd
import cardinal_processor.myw2n as myw2n

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
	cardinals = {}
	val_dict = {'integers': [], 'pos': [], 'weight': []}
	headn_val_dict = {'integers': [], 'pos': [], 'weight': []}
	for idx, item in enumerate(result):
		val = [x for x in item['integers'] if len(x) > 0]
		val_dict['integers'] = val_dict['integers'] + val
		val_dict['pos'] = val_dict['pos'] + [idx+1 for _ in range(0, len(val))]

		val = [x['val'][0] for x in item['headn_match'] if len(x['val']) >0]
		headn_val_dict['integers'] = headn_val_dict['integers'] + val
		headn_val_dict['pos'] = headn_val_dict['pos'] + [idx+1 for _ in range(0, len(val))]

	val_dict['weight'] = [1.0/x for x in val_dict['pos']]
	headn_val_dict['weight'] = [1.0/x for x in headn_val_dict['pos']]

	if len(val_dict['integers']) == 0:
		cardinals['median'] = cardinals['pos_wgt_median'] = ''
	else:
		df = get_dataframe(val_dict)
		
		cutoff = df.weight.sum()/2.0
		cardinals['integers'] = [{'int': x, 'pos': val_dict['pos'][idx]} for idx, x in enumerate(val_dict['integers'])]
		cardinals['pos_wgt_median'] = str(df.integers[df['cumsum'] >= cutoff].iloc[0]) if len(df.integers[df['cumsum'] >= cutoff]) > 0 else ''
		cardinals['median'] = str(math.floor(df.integers.median()))

	if len(headn_val_dict['integers']) == 0:
		cardinals['median_headn'] = cardinals['pos_wgt_median_headn'] = ''
	else:
		df = get_dataframe(headn_val_dict)

		cutoff = df.weight.sum()/2.0
		cardinals['integers_headn'] = [{'int': x, 'pos': headn_val_dict['pos'][idx]} for idx, x in enumerate(headn_val_dict['integers'])]
		cardinals['pos_wgt_median_headn'] = str(df.integers[df['cumsum'] >= cutoff].iloc[0]) if len(df.integers[df['cumsum'] >= cutoff]) > 0 else ''
		cardinals['median_headn'] = str(math.floor(df.integers.median()))

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
	return integers

"""
function to return integers and their corresponding noun phrases for matched predicates
"""
def get_nummodifiers(doc, query_nounphrase=None):
	cardinal_list = []
	text_nounphrase = []
	# get list of cardinal texts
	text_cardinals = [{'text': ent.text, 'id': idx} for idx, ent in enumerate(doc.ents) if ent.label_ == 'CARDINAL']
	# filter noun phrases
	for chunk in doc.noun_chunks:
		# check for cardinals
		if any(a['text'] in chunk.text for a in text_cardinals):
			if query_nounphrase is not None:
				# keep noun phrase with matching phraseword
				if len(chunk.root.text) > 0:
					sim = max([x.similarity(chunk.root) for x in query_nounphrase])
				else:
					sim = 0
				if sim > 0.5:
					cardinal_list.append({'val': get_word_to_num([{'text': chunk.text}]), 'text': chunk.text, 'sim': str(sim)})
	# text_nounphrase = [item for item in text_nounphrase if any(a['text'] in item['text'] for a in text_cardinals)]
	
	# cardinal_list = [{'val': get_word_to_num([item]), 'text': item['text']} for item in text_nounphrase]
	return cardinal_list