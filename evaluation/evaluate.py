import pandas as pd

def evaluate(analysisfile):
	# get count precision
	# metric = pd.DataFrame()
	results = pd.read_csv(analysisfile)
	numrows = len(results)
	results['precision_50'] = results['answer_gold'] == results['50_hnoun']
	results['precision_10'] = results['answer_gold'] == results['10_hnoun']
	results['correctness_ratio_50'] = results.apply(lambda x: x['answer_gold']/x['50_hnoun'] if x['50_hnoun'] > x['answer_gold'] else x['50_hnoun']/x['answer_gold'], axis=1)
	results['correctness_ratio_10'] = results.apply(lambda x: x['answer_gold']/x['10_hnoun'] if x['10_hnoun'] > x['answer_gold'] else x['10_hnoun']/x['answer_gold'], axis=1)
	results.to_csv('metric_'+analysisfile.split('/')[-1].split('_')[-1].split('.csv')[0]+'.csv', encoding='utf-8', index=False)
	return


if __name__ == '__main__':
	# give full path of analysis file
	analysisfile = '/home/shrestha/Documents/PhD/counqer/query_analysis/query_analysis_4.csv'
	evaluate(analysisfile)
