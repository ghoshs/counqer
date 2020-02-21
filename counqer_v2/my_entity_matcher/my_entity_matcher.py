import nltk
import spacy
from spacy.tokens import Doc, Token, Span
from spacy.matcher import PhraseMatcher

# from collections import Counter
# nlp = spacy.load("en_core_web_sm")

# global num_api_calls
# num_api_calls = 0 

class MYSpacyDoc():

	name = "entity_matcher"

	def __init__(self, nlp, query_tags):

		self.nlp = nlp

		self.query_tags = query_tags
		# patterns = [nlp(item) for item in self.query_tags]
		# self.matcher = PhraseMatcher(nlp.vocab)
		# self.matcher.add("QTERMS", None, *patterns)

		Token.set_extension("is_ent_match", default=0, force=True)
		Span.set_extension("is_ent_match", getter=self.span_is_ent_match, force=True)
		Doc.set_extension("has_ent_match", getter=self.doc_has_ent_match, force=True)

	def __call__(self, doc):

		# matches = self.matcher(doc)
		# print('matches: ', matches)
		flag = None
		for ent in doc.ents:
			
			for q_ent in self.query_tags.ents:
				sim = q_ent.similarity(ent)
				if sim > 0.5 and ent.label_ == q_ent.label_:
					if flag is not None and sim < flag:
						continue
					for idx in range(ent.start, ent.end):
						doc[idx]._.set('is_ent_match', sim)
					flag = sim
			# if any([ent.start >= start and ent.end <= end  for _, start, end in matches]):
			# 	for idx in range(ent.start, ent.end):
			# 		doc[idx]._.set("is_ent_match", True)
			# 		flag = True
			# 	# ent._.set("has_ent_match", True)
		if flag is not None:
			assert doc._.has_ent_match
		else:
			assert not doc._.has_ent_match
		return doc

	def span_is_ent_match(self, tokens):
		return max([t._.get("is_ent_match") for t in tokens])

	def doc_has_ent_match(self, tokens):
		return any([t._.get("is_ent_match") for t in tokens])


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