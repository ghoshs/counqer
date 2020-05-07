import requests
import csv
from tqdm import tqdm
import create_ftq_queries as cfq
import argparse
from collections import defaultdict
import pandas as pd
import numpy as np
# ## server edits - 2 ##

# ## server edits ##
# http_proxy = 'http://dmz-gw.mpi-klsb.mpg.de:3128'
# https_proxy = 'https://dmz-gw.mpi-klsb.mpg.de:3128'

def create_outfile(outfile, header):
	try:
		open(outfile)
	except FileNotFoundError:
		with open(outfile, 'w') as csvfile:
			writer = csv.DictWriter(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL, fieldnames=header)
			writer.writeheader()

def get_median_results(cardinal_stats, val, rowbuffer):
	# median_labels = {'median': val+'_median', 'pos_wgt_median': val+'_median_pos', 
					 # 'median_headn': val+'_hnoun', 'pos_wgt_median_headn': val+'_hnoun_pos'}
	median_labels = {'median': val+'_median', 'median_headn': val+'_hnoun'}
	for label in median_labels:
		rowbuffer[median_labels[label]] = int(cardinal_stats[label]) if len(cardinal_stats[label]) > 0 else None

	if 'integers' in cardinal_stats:
		rowbuffer[val+'_cardinals'] = '{'+','.join([item['int'] for item in cardinal_stats['integers']])+'}'
	if 'text_headn' in cardinal_stats:
		rowbuffer[val+'_hnoun_list'] = '{'+','.join([str(item['int'])+ ': "' +cardinal_stats['text_headn'][idx]+'"' for idx,item in enumerate(cardinal_stats['integers_headn'])]) + '}'
		hnoun_freq_dict = defaultdict(int)
		amod_freq_dict = defaultdict(int)
		for hnoun in cardinal_stats['root_headn']:
			hnoun_freq_dict[hnoun] += 1
		for amod in cardinal_stats['amod_headn']:
			for item in amod.split(','):
				amod_freq_dict[item] += 1
		rowbuffer[val+'_hnoun_freq'] = '{'+','.join([str(hnoun_freq_dict[hnoun])+': '+hnoun for hnoun in hnoun_freq_dict]) + '}'
		rowbuffer[val+'_amod_freq'] = '{' + ','.join([str(amod_freq_dict[amod])+': '+amod for amod in amod_freq_dict]) + '}'
	return rowbuffer

def get_entities(result_tags, val, rowbuffer):
	entities = {}
	for item in result_tags:
		for ent in item['ents']:
			if 'np_sim' not in ent:
				continue
			entity = item['text'][ent['start']:ent['end']]
			if entity in entities:
				entities[entity]['freq'] += 1
			else:	
				entities[entity] = {'np_sim': ent['np_sim'], 'freq': 1, 'label': ent['label']}
	rowbuffer[val+'_entities'] = '{' + ','.join([entity + ': (' + entities[entity]['label'] + ',' + str(entities[entity]['freq']) + ',' + 
								 '{:.2f}'.format(entities[entity]['np_sim']) +')' for entity in entities]) + '}'
	return rowbuffer

def aggregator(queryfile='query_templates_ftq.txt', instancefile='instances_ftq.txt', outfile='query_analysis.csv'):
	# queries = cfq.create_ftq_queries(queryfile, instancefile)
	queries = cfq.get_queries()
	header = ['Query', 'answer_gold', 'Google', 'Bing', 
				# '10_median', '10_cardinals', '10_hnoun', '10_hnoun_list', '10_hnoun_freq', '10_amod_freq', '10_entities',
				'50_median', '50_cardinals', '50_hnoun', '50_hnoun_list', '50_hnoun_freq', '50_amod_freq', '50_entities']
	create_outfile(outfile, header)

	# queries = [('How many employees does Diffbot have?',34)]
	## server edits ##
	# url = 'https://counqer.mpi-inf.mpg.de/ftq/ftresults'
	url = 'http://localhost:5000/ftresults'
	snippet_vals = [50] 
	for query, gold in tqdm(queries):
		rowbuffer = {'Query': query, 'answer_gold': str(gold)}
		for val in snippet_vals:
			params = {'query': query, 'snippets': val}
			response = requests.get(url, params=params)
			if response.raise_for_status() is None:
				rowbuffer = get_median_results(response.json()['cardinal_stats'], str(val), rowbuffer)
				rowbuffer = get_entities(response.json()['results_tags'], str(val), rowbuffer)
			else:
				print(query, val, response.raise_for_status())
		with open(outfile, 'a') as csvfile:
			writer = csv.DictWriter(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL, fieldnames=header)
			writer.writerow(rowbuffer)

def has_tc_all(row):
	if pd.isna(row['50_cardinals']):
		return np.nan
	cardinals = row['50_cardinals'][1:-1].split(',')
	cardinals = [int(item) for item in cardinals]
	if int(row['answer_gold']) in cardinals:
		return 1
	else:
		return 0

def has_tc_hnoun(row):
	if pd.isna(row['50_hnoun_list']):
		return 0
	cardinals = row['50_hnoun_list'][1:-1].split(',')
	cardinals = [int(x.split(':')[0]) for x in cardinals if ':' in x]
	if int(row['answer_gold']) in cardinals:
		return 1
	else:
		return 0

def has_noise(row):
	if row['has_tc_hnoun'] == 1:
		if row['answer_gold'] == row['50_hnoun']:
			return 0
		else:
			return 1
	else:
		return 1

def analyser(file = 'query_agg_webisaExact.csv'):
	data = pd.read_csv(file)
	data['has_tc_all'] = data.apply(has_tc_all, axis=1)
	data['has_tc_hnoun'] = data.apply(has_tc_hnoun, axis=1)
	data['has_noise'] = data.apply(has_noise, axis=1)
	data.to_csv('error_analysis.csv', encoding='utf-8', index=False, float_format='%.3f')
	# print avg exact matches, proximity and variance

if __name__ == '__main__':
	# aggregator()
	analyser()
