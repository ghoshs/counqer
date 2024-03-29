'''
This code retrieves query results for 6 cases
case I  : <s1,p1,?o1>; p1 = counting predicate (CP): predC; related predicates are direct enumerating predicates (EP): predE
case II : <s1,p1,?o1>; p1 = CP; related predicates are inverse EP
case III: <s1,p1,?o1>; p1 = direct EP; related predicates are CP
case IV : <s1,p1,?o1>; p1 = inverse EP; related predicates are CP
XXX case V  : <?s1,p1,o1>; p1 = direct EP; related predicates are CP
XXX case VI : <?s1,p1,o1>; p1 = inverse EP; related predicates are CP

## server edits  required: 4 ##

'''

import sys
sys.path.append('/var/www/counqer_v1')

import os
import csv
import pandas as pd
import numpy as np
import re
import json
from SPARQLWrapper import SPARQLWrapper, JSON
try: 
	import urllib2 as myurllib
except ImportError:
	import urllib.request as myurllib

# fname_score_wd = 'static/data/alignments/wikidata.csv'
# fname_score_dbpm = 'static/data/alignments/dbpedia_mapped.csv'
# fname_score_dbpr = 'static/data/alignments/dbpedia_raw.csv'
# fname_wd_prop_label = 'static/data/pred_labels/wikidata_labels.csv'
# fpath_pred_property = 'static/data/pred_property/'
# fpath_set_predicates = 'static/data/set_predicates_old/'

wd_labels = {}

# ## server edits ##
fname_score_wd = '/var/www/counqer_v1/static/data/alignments/wikidata.csv'
fname_score_dbpr = '/var/www/counqer_v1/static/data/alignments/dbpedia_raw.csv'
fname_score_dbpm = '/var/www/counqer_v1/static/data/alignments/dbpedia_mapped.csv'
fname_wd_prop_label = '/var/www/counqer_v1/static/data/pred_labels/wikidata_labels.csv'
fpath_pred_property = '/var/www/counqer_v1/static/data/pred_property/'
fpath_set_predicates = '/var/www/counqer_v1/static/data/set_predicates_old/'

## server edits ##
http_proxy = 'http://dmz-gw.mpi-klsb.mpg.de:3128'
https_proxy = 'https://dmz-gw.mpi-klsb.mpg.de:3128'
myurllib.install_opener(myurllib.build_opener(myurllib.ProxyHandler({'http': http_proxy, 'https': https_proxy})))

# read prednames and map to ID
def get_predID(predicate):
	print('get predID: ',predicate)
	if 'dbp:' in predicate or 'dbo:' in predicate:
		pred = predicate.split(' ')[1][0].lower() + predicate.split(' ')[1][1:] + ''.join([x[0].upper()+x[1:] for x in predicate.split(' ')[2:]])
		if 'dbp:' in predicate:
			pred = 'http://dbpedia.org/property/' + pred
		else:
			pred = 'http://dbpedia.org/ontology/' + pred
	# elif 'dbo:' in predicate:
		# pred = predicate.split(' ')[1] + ''.join([x[0].upper()+x[1:] for x in predicate.split(' ')[2:]])
	elif len(re.findall('P[0-9]+:', predicate)) > 0:
		pred = predicate.split(':')[0]
	return pred

def get_pred_stats(response, kb_name):
	stats = {'response': {}, 'response_inv': {}}
	set_predicates = open(fpath_set_predicates+kb_name+'.json').read()
	# set_predicates = set_predicates.split('jsonCallback(')[1][:-1]
	set_predicates = json.loads(set_predicates)

	data = pd.read_csv(fpath_pred_property+kb_name+'.csv')
	data_inv = pd.read_csv(fpath_pred_property+kb_name+'_inv.csv')

	for item in response['response']:
		if 'error' in item:
			continue
		if 'p2' in item:
			lookup = item['p2']
			lookuptype = 'p2'
		else:
			lookup = response['p1']
			lookuptype = 'p1'
		# if 'dbo:' in lookup or 'dbp:' in lookup:
		# 	lookup = lookup.lower()
		if lookup in set_predicates['predC'] or lookup in set_predicates['predE']:
			pred = get_predID(lookup)
			if 'dbp:' in lookup or 'dbo:' in lookup:
				result = data.loc[data['predicate'] == pred].to_json(orient='records')
			else:
				result = data.loc[data['predicate'].str.endswith(pred)].to_json(orient='records')
			# stats['response'].append({lookuptype: lookup, 'stats': json.loads(result)})
			stats['response'][lookup] = json.loads(result)
			
	for item in response['response_inv']:
		if 'error' in item:
			continue
		if 'p2' in item:
			lookup = item['p2']
			lookuptype = 'p2'
			type = response['get']
		else:
			lookup = response['p1']
			lookuptype = 'p1'
			if 'get' in response:
				type = 'predE' if response['get'] == 'predC' else 'predC'
			else:
				type = None
		# check for inverse predicates
		if type == 'predE' and lookup in set_predicates['predE_inv']:
			pred = get_predID(lookup)
			if 'dbp:' in lookup or 'dbo:' in lookup:
				result = data_inv.loc[data_inv['pred_inv'] == pred].to_json(orient='records')
			else:
				result = data_inv.loc[data_inv['pred_inv'].str.endswith(pred)].to_json(orient='records')
			# stats['response_inv'].append({lookuptype: lookup, 'stats': json.loads(result)})
			stats['response_inv'][lookup]= json.loads(result)
		elif lookup in set_predicates['predE'] or lookup in set_predicates['predC']:
			pred = get_predID(lookup)
			if 'dbp:' in lookup or 'dbo:' in lookup:
				result = data.loc[data['predicate'] == pred].to_json(orient='records')
			else:
				result = data.loc[data['predicate'].str.endswith(pred)].to_json(orient='records')
			# stats['response_inv'].append({lookuptype: lookup, 'stats': json.loads(result)})
			stats['response_inv'][lookup]= json.loads(result)
	print('response sent to pred stats: ', response)
	print('pred stats: ', stats)
	return stats

def o1_and_o2_exist(response, response_inv):
	if 'error' in response and 'error' in response_inv:
		return False
	elif 'error' in response:
		# check if o1Label exists and at least one o2Label is non-empty 
		no_o1Label = 'o1Label' not in response_inv[0]
		idx = 0 if no_o1Label else 1
		no_o2Label = not any(['o2Label' in item and len(item['o2Label']) > 0 for item in response_inv[idx:]])
		# print('1. ',no_o1Label, no_o2Label)
		if no_o1Label and no_o2Label:
			return False
		else:
			return True
	elif 'error' in response_inv:
		# check if o1Label exists and at east one o2Label in response
		no_o1Label = 'o1Label' not in response[0]
		idx = 0 if  no_o1Label else 1
		no_o2Label = not any(['o2Label' in item and len(item['o2Label']) > 0 for item in response[idx:]])
		# print('2. ',no_o1Label, no_o2Label)
		if no_o1Label and no_o2Label:
			return False
		else:
			return True
	elif 'o1Label' not in response[0] and 'o1Label' not in response_inv[0]:
		# no o2Label in response
		no_o2Label_r = not any(['o2Label' in item and len(item['o2Label']) > 0 for item in response[0:]]) 
		# no o2Label in response_inv
		no_o2Label_inv = not any(['o2Label' in item and len(item['o2Label']) > 0 for item in response_inv[0:]])
		# print('3. ',no_o2Label_r, no_o2Label_inv)
		if no_o2Label_r and no_o2Label_inv:
			return False
		else:
			return True
	else:
		return True

def load_wd_plabels():
	global wd_labels
	with open(fname_wd_prop_label) as fp:
		reader = csv.reader(fp, quoting=csv.QUOTE_MINIMAL)
		for row in reader:
			predicate = row[0].split('/')[-1]
			wd_labels[predicate] = predicate + ': ' + row[1].lower()

def beautify_wd_query(url):
	# split at json options
	url = re.split('(sparql\?)|(query=)|(results=json)|(output=json)|(format=json)|(http=)|(https=)',url)
	url = [x for x in url if x is not None and x.startswith(('https://query.wikidata.org', 'SELECT'))]
	# create url similar to wikidata query page
	url = '#'.join(url)
	url = url.replace('+',' ')
	if url.endswith('&'):
		url = url[0:-1]
	return url

def wd_sparql(query, pred_list):
	response = []
	sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
	sparql.setReturnFormat(JSON)
	## server edits
	param = sparql.addParameter('http', http_proxy)
	param = sparql.addParameter('https', https_proxy)
	wd_prefix = 'http://wikidata.org/entity/'
	# idx = 0
	flag_query1 = 0
	for idx, item in enumerate(query):
		sparql.setQuery(item)
		try:
			results = sparql.query().convert()
		except Exception as e:
			print('L78: ', e)
			return({'error': 'Exception in sparql query WD'})
		print('L80: ', results)
		query_vars = results["head"]["vars"]
		o1val = []
		o2val = []
		s1val = []
		s2val = []
		queryurl = beautify_wd_query(sparql.query().response.geturl())
		# if len(results['results']['bindings'][0]) > 0:
		for value in results["results"]["bindings"]:
			if 'o1Label' in value:
				o1val.append(value['o1']['value'] + '/' + value['o1Label']['value'])
			if 'o2Label' in value:
				o2val.append(value['o2']['value'] + '/' + value['o2Label']['value'])
			if 's1Label' in value:
				s1val.append(value['s1']['value'] + '/' + value['s1Label']['value'])
			if 's2Label' in value:
				s2val.append(value['s2']['value'] + '/' + value['s2Label']['value'])
		if len(o1val) > 0:	
			response.append({'o1Label': o1val, 'q': queryurl})
			# print('o1label: ', len(o1val), flag_query1)
		elif len(s1val) > 0:
			response.append({'s1Label': s1val, 'q': queryurl})
		# include empty results also
		# if len(o2val) > 0:
		if len(pred_list[idx]) > 0:
			if 'o2' in query_vars:
				response.append({'o2Label': o2val, 'p2': wd_labels[pred_list[idx].split('_inv')[0]], 'q': queryurl})
			elif 's2' in query_vars:
				response.append({'s2Label': s2val, 'p2': wd_labels[pred_list[idx].split('_inv')[0]], 'q': queryurl})
			
	if len(response) > 0:
		return(response)
	else:
		return({'error': 'Empty SPARQL result'})
	
def query_wd(subID, predID, objID, df_score, inv):
	temp = None
	temp_ranked = None
	query = []
	inv_query = []
	query_pred_list = []
	inv_query_pred_list = []
	response = {}
	responselimit = "1000"

	# pred = ':'.join([x.strip() for x in predID.split(':')])
	pred = predID.split(":")[0]+inv
	# print(df_score['predE'].str.split('/').str[-1].unique())

	# if pred in df_score['predE'].str.extract(r'(P\d+)', expand=False).unique():
	if pred in df_score['predE'].str.split('/').str[-1].unique():
		get = 'predC'
	elif pred in df_score['predC'].str.split('/').str[-1].unique():
		get = 'predE'
	else:
		response['p1'] = predID
		if len(inv) == 0:
			q = """SELECT ?o1 ?o1Label WHERE {
				SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
				OPTIONAL {wd:""" + subID.strip() + """ wdt:""" + predID.split(':')[0] + """ ?o1.}
				} limit """ + responselimit
			print('L161: ', q)
			response['response'] = wd_sparql([q], [''])
			if 'error' not in response['response']:
				response['s1'] = subID
			response['response_inv'] = {'error': 'Empty query'}
		else:
			q = """SELECT ?s1 ?s1Label WHERE {
				SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
				OPTIONAL {?s1 wdt:""" + predID.split(':')[0] + """ wd:""" + subID.strip() + """.}
				} limit """ + responselimit
			response['response_inv'] = wd_sparql([q], [''])
			if 'error' not in response['response_inv']:
				response['o1'] = subID
				response['get'] = 'predC'
			response['response'] = {'error': 'Empty query'}

			print('L170: ', q)
		
		response['error'] = 'No co-occurring pair'
		response['stats'] = get_pred_stats(response, 'wikidata')
		return response
	print('L174: ', 'value get = ', get)
	if 'predC' in get:
		# temp = df_score.loc[df_score['predE'].str.split('/').str[-1].str.split('_').str[0] == pred]
		temp = df_score.loc[df_score['predE'].str.split('/').str[-1] == pred]
		# if len(temp['predE'].unique()) > 1:
		# 	inv = True
		# if inv:
		# 	temp_ranked = temp.sort_values(by='score', ascending=False).groupby('predE').head(5)
			
		# else:
		temp_ranked = temp.sort_values(by='score', ascending=False).head(n=5)

		# if len(objID) == 0:
		# case IV
		if len(inv)>0:
		 # any('inv' in x for x in temp['predE'].unique().tolist()):
			inv_query.append("""SELECT ?o1 ?o1Label WHERE {
				SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
				OPTIONAL {?o1 wdt:""" + predID.split(':')[0] + """ wd:""" + subID.strip() + """.}
				} limit """ + responselimit)
			inv_query_pred_list.append('')
		# case III
		else:
		 # any('inv' not in x for x in temp['predE'].unique().tolist()):
			query.append("""SELECT ?o1 ?o1Label WHERE {
				SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
				OPTIONAL {wd:""" + subID.strip() + """ wdt:""" + predID.split(':')[0] + """ ?o1.}
				} limit """ + responselimit)
			query_pred_list.append('')

		for row in temp_ranked.itertuples():
			# case IV related pred
			if 'inv' in row.predE:
				q = """SELECT ?o2 ?o2Label WHERE {
				SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
				OPTIONAL {wd:""" + subID.strip() + """ wdt:""" + row.predC.split('/')[-1] + """ ?o2.}
				} limit """ + responselimit
				inv_query.append(q)
				inv_query_pred_list.append(row.predC.split('/')[-1])
			else:
			# case IV related pred
				q = """SELECT ?o2 ?o2Label WHERE {
				SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
				OPTIONAL {wd:""" + subID.strip() + """ wdt:""" + row.predC.split('/')[-1] + """ ?o2.}
				} limit """ + responselimit
				query.append(q)
				query_pred_list.append(row.predC.split('/')[-1])
		inv_query_pred_list = [inv_query_pred_list[idx] for idx, q in enumerate(inv_query) if q not in query]
		inv_query = [q for q in inv_query if q not in query]

	elif 'predE' in get:
		temp = df_score.loc[df_score['predC'].str.endswith(pred)]
		temp_ranked = temp.sort_values(by='score', ascending=False).head(n=5)
		# case I/II
		query.append("""SELECT ?o1 ?o1Label WHERE {
				SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
				OPTIONAL {wd:""" + subID.strip() + """ wdt:""" + predID.split(':')[0] + """ ?o1.}
				} limit """ + responselimit)
		query_pred_list.append('')
		for row in temp_ranked.itertuples():
			# case II related pred
			if 'inv' in row.predE:
				q = """SELECT ?s2 ?s2Label WHERE {
				SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }\
				OPTIONAL {?s2 wdt:""" + row.predE.split('/')[-1].split('_inv')[0] + """ wd:""" + subID.strip() + """.}
				} limit """ + responselimit
				inv_query.append(q)
				inv_query_pred_list.append(row.predE.split('/')[-1])
			# case I related pred
			else:
				q = """SELECT ?o2 ?o2Label WHERE {
				SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
				OPTIONAL {wd:""" + subID.strip() + """ wdt:""" + row.predE.split('/')[-1] + """ ?o2.}
				} limit """ + responselimit
				query.append(q)
				query_pred_list.append(row.predE.split('/')[-1]) 
	print('L291: ', temp_ranked[['predE', 'predC']])
	print('L292: ', '\n'.join(query))
	print('L293: ', '\n'.join(inv_query))
	
	if len(query) > 0:
			response['response'] = wd_sparql(query, query_pred_list)
	if len(inv_query) > 0:
			response['response_inv'] = wd_sparql(inv_query, inv_query_pred_list)
	
	if 'response' not in response:
		response['response'] = {'error': 'Empty query'}
	if 'response_inv' not in response:
		response['response_inv'] = {'error': 'Empty query'}
	response['p1'] = predID
	response['get'] = get
	# if len(objID) > 0:
	# 	response['o1'] = objID
	# else:
	response['s1'] = subID
	if not o1_and_o2_exist(response['response'], response['response_inv']):
		response['error'] = 'No instantiation'
	# get pred stats before returning 
	response['stats'] = get_pred_stats(response, 'wikidata')
	return response

def get_dbp_plabel(pred):
	if 'http://dbpedia.org/ontology/' in pred:
		namespace = 'dbo: '
		p_label = pred.split('http://dbpedia.org/ontology/')[-1].split('_inv')[0]
	else:
		namespace = 'dbp: '
		p_label = pred.split('http://dbpedia.org/property/')[-1].split('_inv')[0]

	p_label = p_label[0].upper() + p_label[1:]
	if len(re.findall('[A-Z][^A-Z]*', p_label)) > 0:
		p_label = ' '.join(re.findall('[A-Z][^A-Z]*', p_label))
		p_label = p_label.lower()

	return namespace+p_label

def beautify_dbp_query(url):
	url = re.split('(SELECT)|(results=json)|(output=json)|(format=json)|(http=)|(https=)', url)
	print(url)
	url = [x for x in url if x is not None and (x.startswith('SELECT') or x.endswith(('limit+1000', 'limit+1000&')))]
	url = 'http://dbpedia.org/snorql/?query='+''.join(url)
	if url.endswith('&'):
		url = url[0:-1]
	print(url)
	return url

def dbp_sparql(query, pred_list):
	response = []
	sparql = SPARQLWrapper("http://dbpedia.org/sparql")
	sparql.setReturnFormat(JSON)
	## server edits
	sparql.addParameter('http', http_proxy)
	sparql.addParameter('https', https_proxy)
	prefixes = """PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dbpedia: <http://dbpedia.org/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
	"""
	# idx = 0
	flag_query1 = 0
	for idx, item in enumerate(query):
		sparql.setQuery(prefixes+item)
		try:
			results = sparql.query().convert()
		except Exception as e:
			print('L351: ', e)
			return({'error': 'Exception at sparql query DBP'})
		print('L353: ', results)
		query_vars = results["head"]["vars"]
		o1val = []
		o2val = []
		s1val = []
		s2val = []
		queryurl = beautify_dbp_query(sparql.query().response.geturl())
		print('url: ', queryurl)
		# if len(results['results']['bindings'][0]) > 0:
		for value in results["results"]["bindings"]:
			if 'o1' in value:
				o1val.append(value['o1']['value'])
			if 'o2' in value:
				o2val.append(value['o2']['value'])
			if 's1' in value:
				s1val.append(value['s1']['value'])
			if 's2' in value:
				s2val.append(value['s2']['value'])
		if len(o1val) > 0:
			response.append({'o1Label': o1val, 'q': queryurl})
		elif len(s1val) > 0:
			response.append({'s1Label': s1val, 'q': queryurl})
		# # Include empty responses also for related predicate (pred_list[idx] is non-empty) queries
		if len(pred_list[idx]) > 0:
			p_label = get_dbp_plabel(pred_list[idx])			
			if 'o2' in query_vars:
				response.append({'o2Label': o2val, 'p2': p_label, 'q': queryurl})
			elif 's2' in query_vars:
				response.append({'s2Label': s2val, 'p2': p_label, 'q': queryurl})
	if len(response) > 0:
		return(response)
	else:
		return({'error': 'Empty SPARQL result'})

def query_dbp(subID, predID, objID, df_score, inv):
	temp_ranked = None
	query = []
	inv_query = []
	query_pred_list = []
	inv_query_pred_list = []
	response = {}
	responselimit = "1000"
	namespace = ''

	pred = [x[0].upper()+x[1:] for x in predID.split(' ')[2:]]
	prefix = predID.split(' ')[0]
	# for predicates namespace
	if 'dbp' in prefix:
		namespace = 'http://dbpedia.org/property/'
	elif 'dbo' in prefix:
		namespace = 'http://dbpedia.org/ontology/'
	else:
		prefix = prefix[0:-1]+'/'
		namespace = ''
	pred_query = namespace + predID.split(' ')[1] + ''.join(pred)
	pred = namespace + predID.split(' ')[1] + ''.join(pred) + inv
	# pred = prefix + predID.split(' ')[1] + ''.join(pred)

	if pred in df_score['predE'].unique():
	 # or pred+'_inv' in df_score['predE'].unique():
		get = 'predC'
	elif pred in df_score['predC'].unique():
		get = 'predE'
	else:
		# when co-occuring pair does not exist return only direct result 
		response['p1'] = predID
		if len(inv) == 0:
			q = """SELECT ?o1 WHERE {
					OPTIONAL {<http://dbpedia.org/resource/""" + subID.strip() + """> <""" + pred_query + """> ?o1.}
				} limit """ + responselimit
			print('L441: ', q)
			response['response'] = dbp_sparql([q], [''])
			if 'error' not in response['response']:
				response['s1'] = subID
			response['response_inv'] = {'error': 'Empty query'}
		else:
			q = """SELECT ?s1 WHERE {
					OPTIONAL {?s1 <""" + pred_query + """> <http://dbpedia.org/resource/""" + subID.strip() + """>.}
				} limit """ + responselimit
			response['response_inv'] = dbp_sparql([q], [''])
			if 'error' not in response['response_inv']:
				response['o1'] = subID
				response['get'] = 'predC'
			response['response'] = {'error': 'Empty query'}
			print('L449: ', q)
		response['error'] = 'No co-occurring pair'
		response['stats'] = get_pred_stats(response, 'dbpedia_mapped') if 'dbo' in prefix else get_pred_stats(response, 'dbpedia_raw')
		return response
	print('L452: ', get, pred)
	# If the queries predicate is enumerable
	if 'predC' in get:
		# temp = df_score.loc[df_score['predE'].str.split('_').str[0] == pred]
		temp = df_score.loc[df_score['predE'] == pred]
		# ranking pairs by pearson corr. If corr value does not exist arrange by PMI.
		# if len(temp['predE'].unique()) > 1:
		# 	inv = True
		# if inv:
		# 	temp_ranked = temp.sort_values(by='score', ascending=False).groupby('predE').head(5)
			
		# else:
		temp_ranked = temp.sort_values(by='score', ascending=False).head(n=5)
			# if pd.isnull(temp_ranked['corr_pearson']).sum() > 0:
				# temp_ranked = temp.sort_values(by='PMI', ascending=False).head(n=5)
		# For a <S,P,?> query
	
		# case IV
		# if any('inv' in x for x in temp['predE'].unique().tolist()):
		if len(inv) > 0:
			inv_query.append("""SELECT ?o1 WHERE {
				OPTIONAL {?o1 <""" + pred_query + """> <http://dbpedia.org/resource/""" + subID.strip() + """>.}
			} limit """ + responselimit)
			inv_query_pred_list.append('')
		# case III
		# if any('inv' not in x for x in temp['predE'].unique().tolist()):
		else:
			query.append("""SELECT ?o1 WHERE {
				OPTIONAL {<http://dbpedia.org/resource/""" + subID.strip() + """> <""" + pred_query + """> ?o1.}
			} limit """ + responselimit)
			query_pred_list.append('')

		for row in temp_ranked.itertuples():
			# case IV related pred
			if 'inv' in row.predE:
				q = """SELECT ?o2 WHERE {
					OPTIONAL {<http://dbpedia.org/resource/""" + subID.strip() + """> <""" + row.predC + """> ?o2.}
				} limit """ + responselimit
				inv_query.append(q)
				inv_query_pred_list.append(row.predC)
			# # case III related pred
			else:
				q = """SELECT ?o2 WHERE {
					OPTIONAL {<http://dbpedia.org/resource/""" + subID.strip() + """> <""" + row.predC + """> ?o2.}
				} limit """ + responselimit
				query.append(q)
				query_pred_list.append(row.predC)
		inv_query_pred_list = [inv_query_pred_list[idx] for idx, q in enumerate(inv_query) if q not in query]
		inv_query = [q for q in inv_query if q not in query]

	# If queries predicate is enumerating <S,predE,?o>
	elif 'predE' in get:
		temp = df_score.loc[df_score['predC'] == pred]
		temp_ranked = temp.sort_values(by='score', ascending=False).head(n=5)
		# if pd.isnull(temp_ranked['corr_pearson']).sum() > 0:
			# temp_ranked = temp.sort_values(by='PMI', ascending=False).head(n=5)
		# case I/II
		query.append("""SELECT ?o1 WHERE {
			OPTIONAL {<http://dbpedia.org/resource/""" + subID.strip() + """> <""" + pred_query + """> ?o1.}
		} limit """ + responselimit)
		query_pred_list.append('')

		for row in temp_ranked.itertuples():
			# case II related pred
			if 'inv' in row.predE:
				q = """SELECT ?s2 WHERE {
					OPTIONAL {?s2 <""" + row.predE.split('_inv')[0] + """> <http://dbpedia.org/resource/""" + subID.strip() + """>.}
				} limit """ + responselimit
				inv_query.append(q)
				inv_query_pred_list.append(row.predE)
			# case I related pred
			else:
				q = """SELECT ?o2 WHERE {
					OPTIONAL {<http://dbpedia.org/resource/""" + subID.strip() + """> <""" + row.predE + """> ?o2.}
				} limit """ + responselimit
				query.append(q)
				query_pred_list.append(row.predE)
		
	print('L566: ', temp_ranked[['predE', 'predC']])
	print('L567: ', "\n".join(query))
	print('L568: ', "\n".join(inv_query))
	if len(query) > 0:
		response['response'] = dbp_sparql(query, query_pred_list)

	if len(inv_query) > 0:
			response['response_inv'] = dbp_sparql(inv_query, inv_query_pred_list)
	
	if 'response' not in response:
		response['response'] = {'error': 'Empty query'}
	if 'response_inv' not in response:
		response['response_inv'] = {'error': 'Empty query'}
	response['p1'] = predID
	response['get'] = get
	response['s1'] = subID
	if not o1_and_o2_exist(response['response'], response['response_inv']):
		response['error'] = 'No instantiation'
	# get pred stats before returning 
	if 'dbo' in prefix:
		response['stats'] = get_pred_stats(response, 'dbpedia_mapped')
	elif 'dbp' in prefix:
		response['stats'] = get_pred_stats(response, 'dbpedia_raw')
	return response	

# populate predC, predE predicate pair scores dpeending on KB
def related_predicate(option, subID, predID, objID = None):
	fname_score_by_E = ''
	inv = ''
	if option == 'wikidata':
		fname_score = fname_score_wd
	elif option == 'dbpedia_raw':
		fname_score = fname_score_dbpr
	else:
		fname_score = fname_score_dbpm

	df_score = pd.read_csv(fname_score)
	if predID.endswith('(inv)'):
		predID = predID.split(' (inv)')[0]
		inv = '_inv'
	if option == 'wikidata':
		if len(wd_labels) == 0:
			load_wd_plabels()
		return query_wd(subID, predID, objID, df_score, inv)
	else:
		return query_dbp(subID, predID, objID, df_score, inv)