import sys
import spacy
import pprint
#### server edit
sys.path.append('/var/www/counqer_v2')
# sys.path.append('/home/shrestha/Documents/PhD/counqer/counqer_v2')

from bing_search.bing_search import call_bing_api
import my_entity_matcher.my_entity_matcher as my_ner
from cardinal_processor.cardinal_processor import get_cardinal_stats, get_word_to_num, get_nummodifiers
from text_preprocessor.text_preprocessor import clean_text
from instance_enumerator.instance_enumerator import get_enumerations 
def text_tags(query, max_results=10):
	result = {}
	q_nlp = spacy.load("en_core_web_sm")
	query_tags = q_nlp(query)
	
	# takes only single query
	results = call_bing_api(query, max_results)
	# pprint.pprint(results)

	# remove unidentified separators.
	for item in results:
		item['snippet'] = clean_text(item['snippet'])
	
	r_nlp = spacy.load("en_core_web_sm")
	ent_matcher = my_ner.MYSpacyDoc(r_nlp, query_tags)
	r_nlp.add_pipe(ent_matcher)
	results_tags = r_nlp.pipe([item['snippet'] for item in results])

	result['query_tags'] = query_tags.to_json()
	result['results_tags'] = []
	cardinals = []
	text_cardinals = []
	text_nounphrase = []
	query_nounphrase = [chunk.root for chunk in query_tags.noun_chunks]
	for doc in results_tags:
		ent_match = []
		integers = []
		# get list of cardinal texts
		text_cardinals = [{'text': ent.text, 'id': idx} for idx, ent in enumerate(doc.ents) if ent.label_ == 'CARDINAL']
		# get list of noun phrases
		# text_nounphrase =[{'text': chunk.text, 'id': idx} for idx, chunk in enumerate(doc.noun_chunks)]
		# for ent in doc.ents:
			# ent_match.append(float(ent._.get("is_ent_match")))
		# check if cardinal and get the integer equivalent
		integers = get_word_to_num(text_cardinals)
		# keep only those cardinals which have matching head nouns  
		headn_match = get_nummodifiers(doc, query_tags)


		doc_json = doc.to_json()
		doc_has_ent_match = str(doc._.get("has_ent_match"))
		# get noun phrase similarity values
		doc_json = get_enumerations(doc_json, query_tags);
		# add entity similarity values 
		for idx, ent in enumerate(doc.ents):
			doc_json['ents'][idx]['ent_sim'] = float(ent._.get("is_ent_match"))
		# print(doc_json)
		result['results_tags'].append({'text': doc_json['text'], 'ents': doc_json['ents'], 
									   'has_ent_match': doc_has_ent_match})
		cardinals.append({'integers': integers, 'headn_match': headn_match})


	# text_nounphrase = [item for item in text_nounphrase if any(a['text'] in item['text'] for a in text_cardinals)]
	# print(text_nounphrase)
	result['cardinal_stats'] = get_cardinal_stats(cardinals)

	return result