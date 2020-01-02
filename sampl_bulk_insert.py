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
wiki = "sample.json.gz"
total_num = 4#533522#5226713#60283085#30302#60283085

def genbuffer(pagebuffer):
	for entry in pagebuffer:
		page = json.loads(entry)
		for key in page.keys():
			page[key] = json.dumps(page[key])
		page['_index'] = 'account'
		page['_type'] = "_doc"
		yield page
		# pages.append(page)
	# print(pages)

def import_es(wikifile):
	es=Elasticsearch([{'host':'localhost','port':9200}], timeout=50, max_retries=10, retry_on_timeout=True)
	pagebuffer = []
	buffer_size = 2
	for line in os.popen("zcat %s"%wikifile):
		pagebuffer.append(line)
		if len(pagebuffer) >= buffer_size:
			pages=[]
			res = helpers.bulk(es, genbuffer(pagebuffer))
			print(res)
			pagebuffer = []
	#res = es.index(index=, doc_type = "wiki", body=page)

# pbar = tqdm(total=total_num)

# def procducer(q, wikifile, pbar):
# 	begin_record = False
# 	cnt = 0
# 	print("processing...")
# 	for line in os.popen("zcat %s"%wikifile):
# 		pbar.update(max(cnt - q.qsize() - pbar.n, 0))
# 		q.put(line)
# 		cnt += 1
# 		pbar.set_description("Queue Remain: %s" % q.qsize())
# 	print("total pages: %d", cnt)

# 	for i in range(consumer_n):
# 		q.put(None)
# 	while q.qsize() > 0:
# 		time.sleep(1)
# 		pbar.update(max(cnt - q.qsize() - pbar.n, 0))
# 		pbar.set_description("Queue Remain: %s" % q.qsize())
# 	print("End procducer")


# def consumer(q):
# 	es=Elasticsearch([{'host':'localhost','port':9200}], timeout=50, max_retries=10, retry_on_timeout=True)
# 	pages = []
# 	while True:
# 		res=q.get()
# 		if res == None or len(pages) >= buck_size:
# 			import_es(es, pages)
# 			pages = []
# 		if res is None:
# 			break
# 		pages.append(res)

# 	print("End consumer")


if __name__ == '__main__':
	# q=Queue()
	# p=Process(target=procducer,args=(q, wiki, pbar))
	# p.start()

	# cs = []
	# for _ in range(consumer_n):
	# 	c = Process(target=consumer,args=(q,))
	# 	c.start()
	# 	cs.append(c)


	# p.join()

	# for c in cs:
	# 	c.join()
	# pbar.close()
	import_es(wiki)
	print('Finish Processing.')