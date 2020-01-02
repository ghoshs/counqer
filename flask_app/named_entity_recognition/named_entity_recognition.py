import nltk
import spacy
from spacy.tokens import DocBin
# from spacy import displacy
# import sys
# sys.path.append('/home/shrestha/Documents/PhD/counqer_v2/bing_search')
# from bing_search import call_bing_api

from collections import Counter
nlp = spacy.load("en_core_web_sm")

global num_api_calls
num_api_calls = 0 

def get_tags(text, type='results', engine='bing'):
	if type=='query':
		return nlp(text)

	tags = nlp.pipe([item['snippet'] for item in text])
	# for doc in tags:
	# 	doc_bin.add(doc)

	return tags

# def main():
# 	query = 'James Garfield children'
# 	max_results = 2

# 	results = call_bing_api(query)
# 	tags = get_tags(results)
# 	query_tags = get_tags(query, type='query')
# 	for idx, doc in enumerate(tags):
# 		if idx == max_results:
# 			break
# 		displacy.serve(doc, style="ent")

# 		# for token in doc:
# 		# 	print(token.text, token.ent_iob_, token.ent_type_, token.pos_)
# 	print([(token.text, token.ent_iob_, token.ent_type_, token.pos_) for token in query_tags])
# 	return
	
# if __name__ == '__main__':
# 	main()