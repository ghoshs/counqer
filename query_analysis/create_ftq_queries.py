import csv

def create_ftq_queries(in_qfile='query_templates_ftq.txt', in_ifile='instances_ftq.txt', out_file='queries_ftq.csv'):
	qlines = open(in_qfile).read().split('\n')
	num_qtemplates = int(qlines[1])
	qtemplates = qlines[2:2+num_qtemplates]

	ilines = open(in_ifile).read().split('\n')
	start_idx = int(ilines[1])
	instance_template = ilines[0].split('Instances ')[1].split(',')
	instance_template = [pos.strip() for pos in instance_template]

	queries = []
	instances = ilines[start_idx+1:]
	for instance in instances:
		instance = [item.strip() for item in instance.split(',')]
		for template in qtemplates:
			q = []
			words = template.split()
			q = [w if w not in instance_template else instance[instance_template.index(w)] for w in words]
			queries.append(' '.join(q))

	return queries

def write_queries(queries, out_file='queries_ftq.csv'):
	header = ['Query']
	queries = [[item] for item in queries]
	with open(out_file, 'w') as fp:
		writer = csv.writer(fp, delimiter=',', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(header)
		writer.writerows(queries)

if __name__ == '__main__':
	queries = create_ftq_queries()
	write_queries(queries)