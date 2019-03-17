import sys
import re
import time

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
	
def common_template(host, url, method, headers, data):

	headers = map(conver_header, headers)
	
	jpl = "\n"
	tpl = "import requests" + jpl
	tpl += "headers = {"+jpl
	tpl += (","+jpl).join(headers)
	tpl += jpl+"}"+jpl
	tpl += "data=':data:'"+jpl
	tpl += "req = requests.:method:('http://:address:', headers=headers, data=data)" + jpl
	tpl += "print req.text" + jpl
	tpl = tpl.replace(":method:", method.lower()) 
	tpl = tpl.replace(":address:", host+url)
	tpl = tpl.replace(":data:", data)
	
	return tpl
	

def banner():

	print("""\n#d(0_0)b  Burp Request Parser\n#https://github.com/germanlm93/burp_request_parser\n#burp-req to python\n""")

def default_exit(text):
	
	sys.exit(text)
	
def parameters():
	
	file_in = sys.argv[1]
	
	return file_in

def read_req(filename):
	
	try:
		with open(filename, "r") as f:
			text = f.read()
	except Exception as e:
		default_exit("[Error] Fail reading file")

	if text == "":
		default_exit("[Error] File is empty")
	
	return text
	
def parse(text):
	
	data = get_data(text)
	host = get_host(text)
	headers = get_headers(text)
	method, url = get_action(text)
	
	return common_template(host, url, method, headers, data)

def show(text):
	
	print(text)

def main():
	
	banner()
	
	if len(sys.argv) == 1:
		default_exit("Usage: burp-req-parser.py req.txt")
	else:
		file_in = parameters()
		text = read_req(file_in)
		result = parse(text)
		show(result)

main()
