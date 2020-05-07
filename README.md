Welcome to the reboot of CounQER - a question answering system for COUNting Quantifiers and Entity-valued pRedicates.
Demo available at [https://counqer.mpi-inf.mpg.de/spo](https://counqer.mpi-inf.mpg.de/spo)

### Installation
1. Local machine
   
   To run the system in your local machine, start a simple HTTPS server and run it on port 9000. This is where the app will access data files. Type the command `python -m SimpleHTTPServer 9000` on the command line to get it running. On another terminal start the flask app using the following lines of code. 
```
cd ~/counqer_v1
python counqerv1.py
```
The app runs on port 5000 which can be changed by editing the port number in the file `counqer.py`.

2. Server setup

   You can also run this app on a web server. Install apache and configure the server. CounQER is already configured with the mod WSGI file. Make necessary changes in the `server edits` sections of the code to replace the paths with your server paths.
   The app is enables by the command `apache2 a2ensite <your-server>`

   	Files with server changes 
   	1. `counqer_v1/get_count_data.py`
   	2. `counqer_v1/static/scripts/myscript.js`

### SPO query and top KB alignments
Based on results from CounQER v1 on identifying set predicates from KB and aligning related set-predicates.
