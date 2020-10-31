import os
import sys
import traceback

while True:
	file = open(sys.argv[1], encoding='utf-8')
	code = file.read()
	file.close()
	try:
		print("Start " + sys.argv[1])
		exec(code)
	except:
		traceback.print_exc()
		print("Error")
	finally:
		file.close()
	print("--> restarting")
