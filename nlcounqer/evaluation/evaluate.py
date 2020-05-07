import pandas as pd
import numpy as np

def get_variance(row, col):
	if pd.isna(row[col]):
		return np.nan

	int_list = row[col][1:-1].split(',')
	if 'cardinals' in col:
		int_list = pd.Series([int(x) for x in int_list])
	else:
		int_list = pd.Series([int(x.split(':')[0]) for x in int_list if ':' in x])

	return int_list.std()


def remove_non_similar(row, col):
	entitystring = row[col]
	entitystring = entitystring.split('),')
	entitystring[-1] = entitystring[-1].split(')}')[0]
	entitystring = [entity for entity in entitystring if float(entity.split(',')[-1]) > 0]
	entitystring = '),'.join(entitystring) + ')}' if len(entitystring) > 0 else ''
	return entitystring
		
def evaluate(analysisfile):
	# get count precision
	# metric = pd.DataFrame()
	results = pd.read_csv(analysisfile)
	numrows = len(results)
	num_snippets = ['50']
	for val in num_snippets:
		# cardinals with matching head nouns
		results['precision_hnoun_'+val] = results.apply(lambda x: 1 if x['answer_gold'] == x[val+'_hnoun'] else 0, axis=1)
		results['correctness_hnoun_'+val] = results.apply(lambda x: x['answer_gold']/x[val+'_hnoun'] if x[val+'_hnoun'] > x['answer_gold'] else x[val+'_hnoun']/x['answer_gold'], axis=1)
		results['std_hnoun_'+val] = results.apply(get_variance, args=(val+'_hnoun_list',), axis=1)
		#  all cardinals
		results['precision_all_'+val] = results.apply(lambda x: 1 if x['answer_gold'] == x[val+'_median'] else 0, axis=1)
		results['correctness_all_'+val] = results.apply(lambda x: x['answer_gold']/x[val+'_median'] if x[val+'_median'] > x['answer_gold'] else x[val+'_median']/x['answer_gold'], axis=1)
		results['std_all_'+val] = results.apply(get_variance, args=(val+'_cardinals',), axis=1)
		results[val+'_entities'] = results.apply(remove_non_similar, args=(val+'_entities',), axis=1)
		
	# keep only answers derived from 50 snippets
	cols = [col for idx, col in enumerate(results) if idx < 2 or any([str(val) in col for val in num_snippets])]
	results[cols].to_csv('metric_'+analysisfile.split('/')[-1].split('_')[-1].split('.csv')[0]+'.csv', encoding='utf-8', index=False, float_format='%.3f')
	return


if __name__ == '__main__':
	# give full path of analysis file
	# evaluate('/home/shrestha/Documents/PhD/counqer/query_analysis/query_analysis_wordnet.csv')
	evaluate('/home/shrestha/Documents/PhD/counqer/query_analysis/query_analysis_webisaSubset.csv')
