import csv

def create_ftq_queries(in_qfile='query_templates_ftq.txt', in_ifile='instances_ftq.txt', out_file='queries_ftq.csv'):
	qlines = open(in_qfile).read().split('\n')
	num_qtemplates = int(qlines[1])
	qtemplates = qlines[2:2+num_qtemplates]

	ilines = open(in_ifile).read().split('\n')
	start_idx = int(ilines[1])
	instance_template = ilines[0].split(',')
	instance_template = [pos.strip() for pos in instance_template]

	queries = []
	instances = ilines[start_idx+1:]
	for instance in instances:
		instance = [item.strip() for item in instance.split(',')]
		for template in qtemplates:
			q = []
			words = template.split()
			q = [w if w not in instance_template else instance[instance_template.index(w)] for w in words]
			queries.append((' '.join(q),str(instance[0])))

	return queries

def write_queries(queries, out_file='queries_ftq.csv'):
	header = ['Query', 'Gold']
	queries = [[query, gold] for query, gold in queries]
	with open(out_file, 'w') as fp:
		writer = csv.writer(fp, delimiter=',', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(header)
		writer.writerows(queries)

def get_queries():
	queries = []
	with open('queries_ftq.csv') as fp:
		reader = csv.reader(fp, delimiter=',')
		next(reader)
		for row in reader:
			queries.append((row[0], row[1]))
	return queries

if __name__ == '__main__':
	queries = create_ftq_queries()
	write_queries(queries)