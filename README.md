Welcome to the reboot of CounQER - a question answering system for COUNting Quantifiers and Entity-valued pRedicates.

### Installation
1. Local machine
   
   To run the system in your local machine, start a simple HTTPS server and run it on port 9000. This is where the app will access data files. Type the command `python -m SimpleHTTPServer 9000` on the command line to get it running. On another terminal start the flask app using the following lines of code. 
```
cd ~/flask_app
python counqer.py
```
The app runs on port 5000 which can be changed by editing the port number in the file `counqer.py`.

2. Server setup

   You can also run this app on a web server. Install apache and configure the server. CounQER is already configured with the mod WSGI file. Make necessary changes in the `server edits` sections of the code to replace the paths with your server paths.
   The app is enables by the command 'apache2 a2ensite <your-server>'

### Free Text Search

Location: ./

Wrapper class that returns Bing search results on the requested query and performs NER on the query and search snippets. The annotated results (SpaCy annotations) are then returned as results to the demo page. 

**Note**: Remember to update sys path to correct location of the `flask_app` directory.


 
## Bing Search Results

Location: ./bing_search/

1. bing_search.py - retrieves top n search results from Bing.

## Named Entity Recognition

Location: ./named_entity_recognition/

1. named_entity_recognition.py - uses SpaCy to annotate query and search result snippets. 

2. match_entities.py - 