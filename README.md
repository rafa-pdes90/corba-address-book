Dependencies:

python 3.6

appjar < 1

omniORBpy-4.2.2-win64-python3.6
	Add "lib\python" and "lib\x86_win32" to the environment variable "PYTHONPATH"
	Add "lib\x86_win32" to the environment variable "LD_LIBRARY_PATH"
	Add "bin\x86_win32" to the environment variable "PATH"

---------------#------------------

Start NameService:
First time:
	mkdir C:\Temp
	omninames -start
From second time:
	omninames

start 1 server (localhost:default_port):
	start "" python server.py -ORBInitRef NameService=corbaname::localhost
	
start 1 client (localhost:default_port):
	start "" pythonw client.py -ORBInitRef NameService=corbaname::localhost
