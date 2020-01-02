import sys
import spacy
from spacy import displacy
#### server edit
# sys.path.append('/var/www/flask_app')
sys.path.append('/home/shrestha/Documents/PhD/counqer_v2/flask_app')

from bing_search.bing_search import call_bing_api
from named_entity_recognition.named_entity_recognition import get_tags

def text_tags(query, max_results=2):
	# takes only single query
	results = call_bing_api(query)
	results_tags = get_tags(results)
	query_tags = get_tags(query, type='query')
	for idx, doc in enumerate(results_tags):
		if idx == max_results:
			break
		# displacy.serve(doc, style="ent")

		# for token in doc:
		# 	print(token.text, token.ent_iob_, token.ent_type_, token.pos_)
	# print([(token.text, token.ent_iob_, token.ent_type_, token.pos_) for token in query_tags])
	all_tags = [query_tags]
	for doc in results_tags:
		all_tags.append(doc)
	# html = displacy.render(all_tags, style='ent', minify=True)
	return {'query_tags': query_tags.to_json(), 'results_tags': [displacy.parse_deps(doc) for doc in results_tags]}
	# return displacy.parse_deps(all_tags[1])