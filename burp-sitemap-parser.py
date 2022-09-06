
import re
import sys
import json
import base64
import email
from io import StringIO
import xml.etree.ElementTree as ET

"""
pip install BeautifulSoup4 

"""

class Request:
    # https://stackoverflow.com/questions/41399321/create-a-http-object-from-a-string-in-python
    def __init__(self, request):
        stream = StringIO(request)
        request = stream.readline()

        words = request.split()
        [self.command, self.path, self.version] = words

        self.headers = email.message_from_string(request)
        self.content = stream.read()

    def __getitem__(self, key):
        return self.headers.get(key, '')

def util_convert_data(content):

    return content.decode("utf-8", 'ignore').split("\n")

def util_get_action(content):
	
	action = ""
	
	p = re.compile('^(POST|GET|OPTIONS|PUT|DELETE|TRACE)\s.+\sHTTP.+$')
	for i in util_convert_data(content):
		if action == "":
			if p.match(i):
				action = i
	if(action == ""):
		sys.exit("Action parsing error")
	method = action.split(" ")[0] 
	url = action.split(" ")[1]

	if len(url.split("?")) != 1:
		url = url.split("?")[0]

	return method, url

def util_get_body(content):

	body = ""
	print(content)
	content = content.decode("utf-8", 'ignore')
	if content.find("\r\n\r\n") != -1:
		body = content.split("\r\n\r\n")[1]

	return body

def util_get_json_body(body):

    json_body = None

    try:
        json_body = json.loads(body)
    except ValueError:  # includes simplejson.decoder.JSONDecodeError
        pass
    
    return json_body

# https://www.rfc-editor.org/rfc/rfc7231#section-4.3.3
def util_post_params(content):

    parsed_params = None
    param_regex = re.compile('^(.+=.+&?)*$')
    has_format = param_regex.match(content)
    if has_format:
        parsed_params = {}
        params = content.split("&")
        for param in params:
            pieces = param.split("=")
            if len(pieces) == 2:
                parsed_params[pieces[0]] = pieces[1]

    return parsed_params

def util_get_cookies(header):

    cookies = {}
    cookies = header.split(";")
    for cookie in cookies:
        if cookie.find("=") != -1:
            params = cookie.split("=")
            pairs = zip(params[0::2], params[1::2])
            cookies = dict((k.replace("&", ""),v) for k,v in pairs)

    return cookies


def util_get_params(url):

    parsed_params = {}
    if url.find("?") != -1:
        params = url.split("?")[1]
        params = params.split('&')
        for param in params:
            if url.find("=") != -1:
                pieces = param.split("=")
                if len(pieces) == 2:
                    parsed_params[pieces[0]] = pieces[1]

    return parsed_params

def util_get_host(content):

	host = ""

	p = re.compile('^Host:\s*.+$')
	for i in util_convert_data(content):
		if host == "":
			if p.match(i):
				host = i
	if(host == ""):
		sys.exit("Host parsing error")
	
	return host.split(": ")[1]
		

def util_get_headers(content):

	headers = {}

	p = re.compile('^[a-zA-Z0-9\-\.]+:\s+.+$')
	for i in util_convert_data(content):
		if i.find(": ") != -1:
			h_key = i.split(": ")[0]
			h_val = i.split(": ")[1].strip()
			headers[h_key] = h_val
		x = 1 #print(i)

	return headers



def burp_sitemap_parser():

    print(" == BURP SITEMAP PARSER == \n")

    if len(sys.argv) != 2:
        print("Usage:")
        print("./burp-sitemap-parser.py FILENAME\n")
        sys.exit(0)
    
    filename = sys.argv[1]
    print("[+] parsing " + filename + "\n")

    root = ET.parse(filename).getroot()
    
    found = {}
    input_found = 0
    for child in root:
        content_type = None
        status_code = child.find('status').text
        rq_time = child.find('time').text
        port = child.find('port').text
        protocol = child.find('protocol').text
        print("\n =================================== >>\n")
        url_element = child.find('url')
        # those are base64
        rqs_element = child.find('request[@base64="true"]')
        rss_element = child.find('response[@base64="true"]')
        # decode
        rqs_value = base64.b64decode(rqs_element.text)
        rqs_data_is_json = True
        rqs_data_json = None
        
        body = util_get_body(rqs_value)
        host = util_get_host(rqs_value)
        headers = util_get_headers(rqs_value)
        method, url = util_get_action(rqs_value)
        authorization = "Authorization" in headers.keys()
        cookies = {}
        with_cookies = "Cookie" in headers.keys()
        if with_cookies:
            cookies = util_get_cookies(headers["Cookie"])
        if "Content-Type" in headers:
            content_type = headers['Content-Type']

        
        get_params = util_get_params(url_element.text)
        post_params = util_post_params(body)
        json_body = util_get_json_body(body)
        inputs = []
        print("\033[1mSTATUS CODE:\033[0m " + status_code)
        print("\033[1mTIME:\033[0m " + rq_time)
        print("\033[1mPROTOCOL:\033[0m " + protocol)
        print("\033[1mHOST:\033[0m " + host)
        print("\033[1mPORT:\033[0m " + port)
        print("\033[1mMETHOD:\033[0m " + method)
        print("\033[1mURL:\033[0m " + url)
        print("\033[1mHOST:\033[0m " + host)
        print("\033[1mHEADERS:\033[0m " + ", ".join(sorted(headers.keys())))
        if content_type:
            print("\033[1mCONTENT-TYPE:\033[0m " + content_type)
        total = len(get_params.keys()) 
        
        if type(cookies) is dict:
            print("\033[1mCOOKIES:\033[0m " + ", ".join(cookies.keys()))
            if cookies.keys():
                inputs = inputs + list(cookies.keys())
        if type(get_params) is dict:
            print("\033[1mGET PARAMS:\033[0m " + ", ".join(get_params.keys()))
            if get_params.keys():
                inputs = inputs + list(get_params.keys())
        if type(post_params) is dict:
            print("\033[1mPOST PARAMS:\033[0m " + ", ".join(post_params.keys()))
            if post_params.keys():
                inputs = inputs + list(post_params.keys())

        if type(json_body) is dict:
           print("\033[1mJSON BODY PARAMS:\033[0m " + ", ".join(json_body.keys()))
           if json_body.keys():
                inputs = inputs + list(json_body.keys())

        print("\033[1mLOGIN:\033[0m " + str(authorization))
        if authorization:
            print("\033[1mAUTHORIZATION:\033[0m " + headers["Authorization"])
        print("\033[1mHEADER SUM:\033[0m " + str(len(headers.keys())))
        print("\033[1mINPUT SUM:\033[0m " + str(len(inputs)))
        
        if url not in list(found.keys()):   
            found[url] = inputs
        else:
            add = []
            for inp in inputs:
                if inp not in found[url]:
                    add.append(inp)
            found[url] = inputs + add
  
    print("\n ------------------------------ || ------------------------------\n")  
    print("\033[1mSITEMAP:\033[0m ")    
    out_csv = ""
    rows = []
    for target in list(found.keys()):
        print(" - " + target)
        if len(found[target]) == 0:
            rows.append (",".join([target, ""]))
        else:
            for param in found[target]:
                print("   - " + param)
                rows.append (",".join([target, param]))

    #print("\n\033[1m[+] Inputs ("+str(input_found)+") \033[0m")
    print("\n\033[1m[+] Saving " + filename + '.csv\033[0m')
    with open(filename + '.csv', 'w', encoding='UTF8') as f:
        f.write(",".join(["URL", "PARAMETER"])+"\n")
        f.write("\n".join(rows))


burp_sitemap_parser()
