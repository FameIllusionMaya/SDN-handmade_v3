import sys
from pymongo import MongoClient
while 1:
	print("111111")
try:
	raise KeyboardInterrupt
finally:
	print("Bye")
	sys.exit(MongoClient('localhost', 27017).drop_database('clear_mongo'))