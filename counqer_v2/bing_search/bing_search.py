import requests

# ## server edits ##
# http_proxy = 'http://dmz-gw.mpi-klsb.mpg.de:3128'
# https_proxy = 'https://dmz-gw.mpi-klsb.mpg.de:3128'

def call_bing_api(query, count=10, subscription_key='2faf6a70e52a46318ec658b2a14c891c'):
	# global num_api_calls
	url = "https://api.cognitive.microsoft.com/bingcustomsearch/v7.0/search"
	headers = {'Ocp-Apim-Subscription-Key': subscription_key}
	params = {"q": query, "customconfig": "3701208300", "mkt": "en-US", "safesearch": "Moderate", "responseFilter": "-images,-videos", "count": count}
	response = requests.get(url, headers=headers, params=params)
	
	## server edits ##
	# response = requests.get(url, headers=headers, params=params, proxies={'http': http_proxy, 'https': https_proxy})
	
	response.raise_for_status()
	# num_api_calls += 1
	results = response.json()
	snippets = []
	if 'webPages' in results:
		for rank, item in enumerate(results['webPages']['value']):
			webpage = {}
			webpage['rank'] = rank
			webpage['url'] = item['url'] if 'url' in item else ''
			webpage['about'] = item['about'] if 'about' in item else ''
			webpage['snippet'] = item['snippet'] if 'snippet' in item else ''
			webpage['dateLastCrawled'] = item['dateLastCrawled'] if 'dateLastCrawled' in item else ''
			snippets.append(webpage)
	return snippets

# def main():
# 	query = 'James Garfield children'
# 	subscription_key = '2faf6a70e52a46318ec658b2a14c891c'
# 	# global num_api_calls
# 	# num_api_calls = 0
# 	results = call_bing_api(query, subscription_key)
# 	print(results)

# if __name__ == '__main__':
# 	main()