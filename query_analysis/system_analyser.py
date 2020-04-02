import requests
import csv
from tqdm import tqdm
import create_ftq_queries as cfq
import argparse
from collections import defaultdict

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
	median_labels = {'median_headn': val+'_hnoun'}
	for label in median_labels:
		rowbuffer[median_labels[label]] = int(cardinal_stats[label]) if len(cardinal_stats[label]) > 0 else None

	# if 'integers' in cardinal_stats:
		# rowbuffer[val+'_int_list'] = '{'+','.join([item['int'] for item in cardinal_stats['integers']])+'}'
	if 'text_headn' in cardinal_stats:
		rowbuffer[val+'_hnoun_list'] = '{'+','.join([str(item['int'])+ ': ' +cardinal_stats['text_headn'][idx] for idx,item in enumerate(cardinal_stats['integers_headn'])]) + '}'
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
				entities[entity] = {'np_sim': ent['np_sim'], 'freq': 1}
	rowbuffer[val+'_entities'] = '{' + ','.join([entity + ': {'+ str(entities[entity]['freq']) +','+ '{:.2f}'.format(entities[entity]['np_sim']) +'}' for entity in entities]) + '}'
	return rowbuffer

def analyser(queryfile='query_templates_ftq.txt', instancefile='instances_ftq.txt', outfile='query_analysis.csv'):
	queries = cfq.create_ftq_queries(queryfile, instancefile)

	header = ['Query', 'answer_gold', 'Google', 'Bing', 
				'5_hnoun', '5_hnoun_list', '5_hnoun_freq', '5_amod_freq', '5_entities',
				'10_hnoun', '10_hnoun_list', '10_hnoun_freq', '10_amod_freq', '10_entities',
				'50_hnoun', '50_hnoun_list', '50_hnoun_freq', '50_amod_freq', '50_entities']
	create_outfile(outfile, header)

	## server edits ##
	# url = 'https://counqer.mpi-inf.mpg.de/ftq/ftresults'
	url = 'http://localhost:5000/ftresults'
	snippet_vals = [5,10,50] 
	for q in tqdm(queries):
		rowbuffer = {'Query': q}
		for val in snippet_vals:
			params = {'query': q, 'snippets': val}
			response = requests.get(url, params=params)
			if response.raise_for_status() is None:
				rowbuffer = get_median_results(response.json()['cardinal_stats'], str(val), rowbuffer)
				rowbuffer = get_entities(response.json()['results_tags'], str(val), rowbuffer)
			else:
				print(q, val, response.raise_for_status())
		with open(outfile, 'a') as csvfile:
			writer = csv.DictWriter(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL, fieldnames=header)
			writer.writerow(rowbuffer)


if __name__ == '__main__':
	# parser = argparse.ArgumentParser(description="collect answers for different queries across multiple settings of CounQER.")
	# parser.add_argument('queryfile', help="filename for file containing query templates. \nFormat: \n\tline1: Header. \n\tline2: N denoting the number of templates in followed by 1 template per line for next N lines.")
	# parser.add_argument('instancefile', help="filename for file containing instances to fill query templates: \nFormat: \n\tline1: Header. \n\tline2: Start index for instances followed by 1 instance per line")
	# parser.add_argument('outfile', help="filename for query analysis output")
	# args = vars(parser.parse_args()) 
	# print(args['queryfile'], args['instancefile'], args['outfile'])
	# analyser(args['queryfile'], args['instancefile'], args['outfile'])
	analyser()