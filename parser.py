import sys
import re

def get_action(content):
	action = ""
	p = re.compile('^(POST|GET|PUT|DELETE|TRACE)\s.+\sHTTP.+$')
	for i in content.split("\n"):
		if action == "":
			if p.match(i):
				action = i
	if(action == ""):
		sys.exit("Action parsing error")
	else:
		method = action.split(" ")[0] 
		url = action.split(" ")[1]
	return method, url

def get_host(content):
	host = ""
	p = re.compile('^Host:\s*.+$')
	for i in content.split("\n"):
		if host == "":
			if p.match(i):
				host = i
	if(host == ""):
		sys.exit("Host parsing error")
	else:
		return host.split(": ")[1]
		
def get_headers(content):
	headers = []
	p = re.compile('^[a-zA-Z0-9\-\.]+:\s+.+$')
	for i in content.split("\n"):
		if p.match(i):
			headers.append(i)
	if(headers == []):
		sys.exit("Headers parsing error")
	else:
		return headers

def get_data(content):
	data = ""
	catch = True
	for i in content.split("\n"):
		if catch == True:
			if i.strip() == "": catch = False
		else:
			if data == "": data = i
	return data
	
def conver_header(row):
	headertpl = "\t':key:':':value:'"
	key = row.split(":")[0].lstrip().strip()
	val = row.split(":")[1].lstrip().strip()
	headertpl = headertpl.replace(':key:', key)
	headertpl = headertpl.replace(':value:', val)
	return headertpl
	
def create_client(filename, host, url, method, headers, data):
	jpl = "\n"
	with open(filename, "w"): pass
	reqfile = open(filename, "w")
	filetpl = "import requests" + jpl
	filetpl += "headers = {"+jpl
	headers = map(conver_header, headers)
	filetpl += (","+jpl).join(headers)
	filetpl += jpl+"}"+jpl
	filetpl += "req = requests.:method:('http://:address:', headers=headers)" + jpl
	filetpl += "print req.text" + jpl
	filetpl = filetpl.replace(":method:", method.lower()) 
	filetpl = filetpl.replace(":address:", host+url)
	reqfile.write(filetpl)
	reqfile.close()
	

def main():
	if len(sys.argv) == 1:
		sys.exit("usage parser.py req.txt")
	else:
		filename = sys.argv[1]
		outputname = sys.argv[2] if len(sys.argv)>=3 else "req.py"
		text = ""
		try:
			with open(filename, "r") as f:
				text = f.read()
		except IOError as e:
			sys.exit(e)
		if text == "":
			sys.exit("File is empty")
		method, url = get_action(text)
		host = get_host(text)
		headers = get_headers(text)
		data = get_data(text)
		create_client(outputname, host, url, method, headers, data)

main()
