import os
import sys

while True:
	file = None
	try:
		file = open(sys.argv[1])
		exec(file.read())
	except:
		print("Error")
	finally:
		file.close()
	print("--> restarting")