Welcome to the natural language CounQER - a question answering system for COUNting Quantifiers and Entity-valued pRedicates.

### Installation
1. Local machine
   
   To run the system in your local machine, start a simple HTTPS server and run it on port 9000. This is where the app will access data files. Type the command `python -m SimpleHTTPServer 9000` on the command line to get it running. On another terminal start the flask app using the following lines of code. 
```
cd /path/to/nlcounqer
python nlcounqer.py
```
The app runs on port 5000 which can be changed by editing the port number in the file `counqer.py`.

2. Server setup

   You can also run this app on a web server. Install apache and configure the server. CounQER is already configured with the mod WSGI file. Make necessary changes in the `server edits` sections of the code to replace the paths with your server paths.
   The app is enables by the command `apache2 a2ensite <your-server>`

   	Files with server changes 
   	1. `counqer_v2/free_text_search.py`
   	2. `counqer_v2/static/scripts/myscript.js`
   	3. `counqer_v2/bing_search/bing_search.py`
    4. `counqer_v2/instance_enumerator/instance_enumerator.py`

3. SpaCy models
   
   This system uses `en_core_web_md` model. For faster output at cost of accuracy `en_core_web_sm` may also be used. Models specified in function `text_tags` in file `free_text_search.py` for query and result.

### Free Text Search

Location: ./

`free_text_search.py` - Wrapper function that returns Bing search results on the requested query and performs NER on the query and search snippets. The annotated results (SpaCy annotations) are then returned as results to the demo page. 

**Note**: Remember to update sys path to correct location of the `flask_app` directory.


 
#### Bing Search Results

Location: ./bing_search/

`bing_search.py` - retrieves top n search results from Bing.

#### Named Entity Recognition

Location: ./my_entity_matcher/

`my_entity_matcher.py` - uses SpaCy to annotate query and search result snippets. Additional functionality to link similar entities in the text snippets to the queried entity. 

#### Cardinal Value Processor

Location: ./cardinal_processor/

`cardinal_processor.py` - contains functions to
   a. return all cardinal integers from text
   b. return cardinal integers with following noun phrase if present
   c. return median variations for a list of cardinal integers

`myw2n.py` - modified word to number python package to convert number in word to integer format. 

#### Text preprocessor

Location: ./text_preprocessor/

`text_preprocessor.py` - has function to handle text separator combinations not supported by SpaCy.

#### Query Analyser

Location: ../query_analysis/

`query_templates_ftq.txt` - File contains query templates. 2nd line in file gives the number of templates to consider.

`instances_ftq.txt` - Query instances for evaluation.

`create_ftq_queries.py` - Create NL queries using the templates from `query_templates_ftq.txt` and instances from `instances_ftq.txt`.

`system_analyser.py` - Call the counqer/ftq system to retrieve json results on NL queries and save comprehensive results in `query_analysis_<*id*>.csv`.


#### Filter related enumerations

Location: ./instance_enumerator/

`instance_enumerator.py` - For all named-entities in result snippets, return max path similarity (hyper/hyponymy) of the entity type to the query head-noun. 
<!-- 
### WebIsA

Query text: 
`PREFIX isa: <http://webisa.webdatacommons.org/concept/>
SELECT ?hyponymLabel ?hypernymLabel ?confidence
WHERE{
    GRAPH ?g {
        ?hyponym skos:broader isa:_person_.
    }
    ?hyponym rdfs:label ?hyponymLabel.
    isa:_person_ rdfs:label ?hypernymLabel.
    ?g <http://webisa.webdatacommons.org/ontology#hasConfidence> ?confidence.
    filter(regex(str(?hyponymLabel), "children"))
}
ORDER BY(?confidence)
LIMIT 100` -->

### WordNet

download WordNet data in nltk in the Python venv.

#### Debugging

1. UnicodeDecodeError: 'ascii' codec can't decode byte 0xe2 in position

Check Apache lang configuration. [Is LC_ALL set to utf-8?](https://itekblog.com/ascii-codec-cant-encode-characters-in-position/)

2. counqer.mpi-inf.mpg.de is the main landing page. The html script is at /var/www/html/index.html

3. Modify w2n.py into cardinal_processing/myw2n.py
	a. Able to convert `144 thousand` to integer.
	b. Able to convert `60,000` to integer. 

4. Data cleaning for webIsaDB hyponymy check is a nightmare
  a. Named-entites may or may not be preceded by an `_`
  b. The text to be searched should not contain any special characters.
  c. Text should be in lower case

