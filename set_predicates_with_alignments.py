import pandas as pd
import json
import re

def get_label(p_label):
	p_label = p_label[0].upper() + p_label[1:]
	if len(re.findall('[A-Z][^A-Z]*', p_label)) > 0:
		p_label = ' '.join(re.findall('[A-Z][^A-Z]*', p_label))
	p_label = p_label.lower()

	return p_label

def add_alignment_info():
	alignment_path = './counqer_v1/static/data/alignments/'
	set_predicates_path = './counqer_v1/static/data/set_predicates_old/'
	set_predicates_path_new = './counqer_v1/static/data/set_predicates/'
	
	kb_names = ['dbpedia_mapped', 'dbpedia_raw', 'wikidata']
	for kb in kb_names:
		set_predicates = {'predE': {'aligned': [], 'unaligned': []}, 
						  'predC': {'aligned': [], 'unaligned': []},
						  'predE_inv': {'aligned': [], 'unaligned': []}}
		alignments = pd.read_csv(alignment_path+kb+'.csv', delimiter=',')
		if kb == 'wikidata':
			align_predE = alignments['predE'].str.split('/').str[-1].unique().tolist()
			align_predE_inv = [x.split('_inv')[0] for x in align_predE if x.endswith('_inv')]
			align_predE = [x for x in align_predE if not x.endswith('_inv')]
			align_predC = alignments['predC'].str.split('/').str[-1].unique().tolist()
		else:
			if kb == 'dbpedia_raw':
				splitat = 'http://dbpedia.org/property/'
				prefix = 'dbp: '
			else:
				splitat = 'http://dbpedia.org/ontology/'
				prefix = 'dbo: '
			align_predE = alignments['predE'].str.split(splitat).str[-1].unique().tolist()
			align_predE_inv = [x.split('_inv')[0] for x in align_predE if x.endswith('_inv')]
			align_predE = [x for x in align_predE if not x.endswith('_inv')]
			align_predC = alignments['predC'].str.split(splitat).str[-1].unique().tolist()
			
			align_predE = [prefix+get_label(x) for x in align_predE]
			align_predE_inv = [prefix+get_label(x) for x in align_predE_inv]
			align_predC = [prefix+get_label(x) for x in align_predC]
		
		predicates = json.loads(open(set_predicates_path+kb+'.json').read())
		for item in predicates['predE']:
			if kb == 'wikidata':
				pred = item.split(":")[0]
				if pred in align_predE:
					set_predicates['predE']['aligned'].append(item)
				else:
					set_predicates['predE']['unaligned'].append(item)
			else:
				if item in align_predE:
					set_predicates['predE']['aligned'].append(item)
				else:
					set_predicates['predE']['unaligned'].append(item)
		
		for item in predicates['predE_inv']:
			if kb == 'wikidata':
				pred = item.split(":")[0]
				if pred in align_predE_inv:
					set_predicates['predE_inv']['aligned'].append(item)
				else:
					set_predicates['predE_inv']['unaligned'].append(item)
			else:
				if item in align_predE_inv:
					set_predicates['predE_inv']['aligned'].append(item)
				else:
					set_predicates['predE_inv']['unaligned'].append(item)
		
		for item in predicates['predC']:
			if kb == 'wikidata':
				pred = item.split(":")[0]
				if pred in align_predC:
					set_predicates['predC']['aligned'].append(item)
				else:
					set_predicates['predC']['unaligned'].append(item)
			else:
				if item in align_predC:
					set_predicates['predC']['aligned'].append(item)
				else:
					set_predicates['predC']['unaligned'].append(item)
		
		with open(set_predicates_path_new+kb+'.json', 'w') as fp:
			fp.write(json.dumps(set_predicates))
		

if __name__ == '__main__':
	add_alignment_info()