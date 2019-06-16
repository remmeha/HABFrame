import socket
import io
import sys
import threading
import time
import sys
import os
from flask import Flask, request
from flask import make_response, send_file
from flask_cors import CORS

PATH=os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH + "/classes")
sys.path.append(PATH + "/classes/general")
sys.path.append(PATH + "/data")
from HABframe_main import habframe_main
from settings import Settings
from logger import Logging

##load settings
settings_class = Settings()
port = settings_class.get_setting("main", "port")

main = habframe_main()
logging = Logging()

app = Flask("HABFrame", template_folder=PATH + '/templates', static_folder=PATH+"/static")
CORS(app)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):   
    env = get_env(request)
    key = get_key(env)
    response = main.process_request(env)
    return format_response(response)

def get_env(request):
    url = request.url[request.url.find(request.path)+1:]
    if request.path == "/":
        url = "/"
    return { "PATH_INFO": url }

def get_key(env):
    request_split = env["PATH_INFO"].replace("%20", " ").split('?')
    request_list = request_split[0].replace("%20", " ").split('/')
    if request_list[0] == "backend":
        try:
            logging.debug("Backend session key detected: " + str(request_list[1]), location="server")
            return request_list[1]
        except:
            pass
    ##not backend, try cookie
    return request.cookies.get("HomeServer")
    
def format_response(response):
    if response[0] == False:
        self.logging.error("Invalid request, no response generated", location="server")
        return "no response", 404
    elif response[0] == "bytedata":
        return send_file(
            io.BytesIO(response[1]),
            mimetype='image/jpeg')
    else:
        resp = make_response(response[1])
        if response[2] != False:
            cd = { "Path": "/", "value": response[2][0] }
            if response[2][1]:
                exp = response[2][1].strftime("%a, %d %b %Y %H:%M:%S GMT")
            else:
                exp = None
            resp.set_cookie("HomeServer", response[2][0],  path="/", expires = exp)
        return resp

@app.template_filter('get_block')
def template_filter(block, filename, **kwargs):
    html = render_template(filename, **kwargs)
    # Then use regex or something to parse
    # or even simple splits (better with named blocks), like...
    content = html.split('{%% block %s %%}'%(block))[-1]
    content = content.split('{%% endblock %%}')[0]
    return content

app.run(host='0.0.0.0', port=int(port))


