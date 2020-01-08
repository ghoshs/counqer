import sys
import spacy
from spacy import displacy
#### server edit
# sys.path.append('/var/www/flask_app')
sys.path.append('/home/shrestha/Documents/PhD/counqer_v2/flask_app')

from bing_search.bing_search import call_bing_api
import my_entity_matcher.my_entity_matcher as my_ner

def text_tags(query, max_results=10):
	result = {}
	q_nlp = spacy.load("en_core_web_sm")
	query_tags = q_nlp(query)
	
	# takes only single query
	results = call_bing_api(query, max_results)
	# print(results)
	r_nlp = spacy.load("en_core_web_sm")
	ent_matcher = my_ner.MYSpacyDoc(r_nlp, query_tags)
	r_nlp.add_pipe(ent_matcher)
	results_tags = r_nlp.pipe([item['snippet'] for item in results])

	result['query_tags'] = query_tags.to_json()
	result['results_tags'] = []
	for doc in results_tags:
		ent_match = []
		for ent in doc.ents:
			ent_match.append(float(ent._.get("is_ent_match")))
		doc_json = doc.to_json()
		doc_has_ent_match = str(doc._.get("has_ent_match"))
		result['results_tags'].append({'text': doc_json['text'], 'ents': doc_json['ents'], 'has_ent_match': doc_has_ent_match, 'ent_similarity': ent_match})

	return result
	# return displacy.parse_deps(all_tags[1])