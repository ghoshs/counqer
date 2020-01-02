from multiprocessing import Process,Queue, Pool
import bz2, sys
from tqdm import tqdm
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from multiprocessing import Pool
import io, os
import json
import time


consumer_n = 20
buck_size = 40
wiki = "enwiki-20191020-pages-articles-multistream.json.gz"
total_num = 533522#5226713#60283085#30302#60283085

def genbuffer(pagebuffer):
	for entry in pagebuffer:
		page = json.loads(entry)
		for key in page.keys():
			page[key] = json.dumps(page[key])
		page['_index'] = 'vanilla'
		page['_type'] = "_doc"
		yield page
		# pages.append(page)
	# print(pages)

def import_es(wikifile):
	es=Elasticsearch([{'host':'localhost','port':9200}], timeout=50, max_retries=10, retry_on_timeout=True)
	pagebuffer = []
	buffer_size = 1000
	for line in tqdm(os.popen("zcat %s"%wikifile)):
		pagebuffer.append(line)
		if len(pagebuffer) >= buffer_size:
			pages=[]
			res = helpers.bulk(es, genbuffer(pagebuffer), stats_only=True, raise_on_exception=False)
			print(res)
			pagebuffer = []

if __name__ == '__main__':
	import_es(wiki)
	print('Finish Processing.')