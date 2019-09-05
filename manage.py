from flask import Flask, request, abort
import subprocess, os, socket, pymysql, shutil, time, psutil, json
from setting_blk import block1, block2, block3, block4, block5
from flask_basicauth import BasicAuth
from pymysql.err import IntegrityError

db_server = 'localhost'
db_uname = 'admin'
db_pass = 'password'
db_name = 'db'

user = "admin"
passwd = "password"

app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = user
app.config['BASIC_AUTH_PASSWORD'] = passwd
basic_auth = BasicAuth(app)


def db_connect():
	try:
		return pymysql.connect(db_server, db_uname, db_pass, db_name)
	except:
		print "Database connection failed"
		return False


def get_port(username):
	db = db_connect()
	cursor = db.cursor()
	if cursor.execute("SELECT port FROM users WHERE username = '%s'" %username):
		port = cursor.fetchall()[0][0]
		cursor.close()
		db.close()
		return port
	return False


@app.route('/', methods = ['POST', 'DELETE', 'PUT'])
@basic_auth.required
def user():
	data = request.get_json(force=True)
	if not data.has_key("username"):
		return json.dumps({"code":400, "message":"Username required", "status":0})
	username = data["username"].lower()
	#if not username.isalnum():
	#	return json.dumps({"code":400, "message":"Invalid Username", "status":0})
	if not set(data.keys()).issubset(["username", "password"]):
		return json.dumps({"code":400, "message":"Invalid arguments", "status":0})
	path = "/root/api/instances/"
	if request.method == "POST" or request.method == "PUT":
		if not data.has_key("password") or data["password"] == "":
			return json.dumps({"code":400, "message":"Password required", "status":0})
		password = data["password"]
	if request.method == "POST":
		sock = socket.socket()
		sock.bind(('localhost', 0))
		port = str(sock.getsockname()[1])
		db = db_connect()
		if not db:
			return json.dumps({"code":400, "message":"Database connection failed", "status":0})	
		cursor = db.cursor()
		if cursor.execute("select port from users"):
			result = cursor.fetchall()
			while (port, ) in result:
				sock.bind(('localhost', 0))
                		port = str(sock.getsockname()[1])
		sock.close()
		try:
			cursor.execute("insert into users (username, password, port) values ('%s', '%s', '%s')" %(username, password, port))
		except IntegrityError:
			return json.dumps({"code":409, "message":"Username already exists", "status":0})
		except:
			return json.dumps({"code":500, "message":"Unable to insert into database", "status":0})
		db.commit()
		db.close()

		try:
			os.makedirs(path + username + "/modules")
			subprocess.check_output(["cp", path+"settings.js", path+username+"/"])
		except Exception as e:
			print str(e)
		os.chdir(path + username)
		settings_js = open("settings.js", "w")
		flow_block = "flowFile: 'flows_%s.json'," %username
		hroot_block = "httpRoot: '/" + username + "',"
		auth_block = '''adminAuth: {
		sessionExpiryTime: 3600,
        type: "credentials",
        users: [{
            	username: "%s",
            	password: "%s",
            	permissions: "*"
        		}]
    	},''' %(username, password)
		httpAuth_block = "httpNodeAuth:{user:'%s',pass:'%s'}," %(username, password)
		w_content = block1 + flow_block + block2 + hroot_block + block3 + auth_block + block4 + httpAuth_block + block5
		settings_js.write(w_content)
		settings_js.close()
		nginx_file = "nginx.d/" + username + ".conf"
		os.chdir(path)
		nginx_h = open(nginx_file, "w")
		usr_blk = '''location /%s/ {
			if ($scheme = http) {
				return 301 https://$server_name$request_uri;
    		    }
	    	    proxy_pass http://127.0.0.1:%s/%s/;
	    	    proxy_set_header Host $host;
	    	    proxy_set_header X-Real-IP $remote_addr;
	    	    proxy_http_version 1.1;
	    	    proxy_set_header Upgrade $http_upgrade;
	    	    proxy_set_header Connection "upgrade";
	    	}
		''' %(username, str(port), username)
		nginx_h.write(usr_blk)
		nginx_h.close()
		os.chdir(path + username + "/")
		start_instance(username, port)
#		try:
#			subprocess.Popen(["nohup", "node-red", "-s", path + username + "/settings.js", "-u", path + username + "/", "-p", port], preexec_fn=os.setpgrp, close_fds=True)
#		except Exception as e:
#			return "Problem starting node-red"
		try:		
			subprocess.check_output(["systemctl","reload", "nginx"])
		except Exception as e:
			return "Nginx reload failed" + "\n" + str(e)	
		return json.dumps({"message":"User created successfully.", "code":200, "status":0}), 200
	elif request.method == 'DELETE':
		data = request.get_json(force=True)
		try:
			db = db_connect()
		except:
			return "Database connection failed"
		cursor = db.cursor()
		if cursor.execute("DELETE FROM users WHERE username = '%s'" %username):
			db.commit()
			db.close()
		else:
			db.close()
			return json.dumps({"code":400, "message":"Username does not exist", "status":1}), 200
		try:
			shutil.rmtree(path + username)
		except OSError as e:
			print "\n\nPath does not exist\n\n"
		if stop_instance() == True:
			print "\n\nInstance not Running\n\n" 
		try:
			os.remove(path + "nginx.d/" + username + ".conf")
		except:
			print "\n\nNo such file found\n\n"
		subprocess.check_output(["systemctl", "reload", "nginx"])					
		return json.dumps({"message":"User deleted", "status":0, "code":200}), 200
	elif request.method == 'PUT':
		db = db_connect()
		cursor = db.cursor()
		if cursor.execute("UPDATE users SET password = '%s' WHERE username = '%s'" %(password, username)):
			port = get_port(username)
			db.commit()
			db.close()
		else:
			return json.dumps({"code":200, "status":1, "message":"User not found"}), 200

		os.chdir(path + username)
		settings_js = open("settings.js", "w")
		flow_block = "flowFile: 'flows_%s.json'," %username
		hroot_block = "httpRoot: '/" + username + "',"
		auth_block = '''adminAuth: {
		sessionExpiryTime: 3600,
        type: "credentials",
        users: [{
            	username: "%s",
            	password: "%s",
            	permissions: "*"
        		}]
    	},''' %(username, password)
		httpAuth_block = "httpNodeAuth:{user:'%s',pass:'%s'}," %(username, password)
		w_content = block1 + flow_block + block2 + hroot_block + block3 + auth_block + block4 + httpAuth_block + block5
		settings_js.write(w_content)
		settings_js.close()
		stop_instance(port)
		start_instance(username, port)
		return json.dumps({"message":"Password updated successfully", "status":1, "code":200})


@basic_auth.required
@app.route('/list', methods = ['GET'])
def list_users():
	db = db_connect()
	if not db:
		return json.dumps({"status":1, "message":"Database connection failed", "code":500})
        cursor = db.cursor()
        if cursor.execute("SELECT username, port FROM users"):
        	res_data = cursor.fetchall()
		result = {}
               	for row in res_data:
			result[row[0]] = row[1]
                db.close()
		return json.dumps({"status":0, "message":"SUCCESS","data":result, "code":200}), 200
	else:
		return json.dumps({"message":"\nUnable to retrieve data\n", "code":200, "status":1}), 200



@basic_auth.required
@app.route('/instance', methods = ['POST', 'GET'])
def instance_actions():
	path = "/root/api/instances/"
	data = request.get_json(force=True)
	if "username" not in data.keys():
		return json.dumps({"status":1, "message":"Username required", "code":"400"}) + "\n", 200
	username = data["username"].lower()
	if username == "":
		return json.dumps({"status":1, "message":"Username required", "code":"400"}) + "\n", 200
	action = data.setdefault("action", "status")
	if action not in ["start", "stop", "restart", "status"]:
		return json.dumps({"status":1, "message":"Not a valid action", "code":200}), 200
	port = str(get_port(username))
	if not port:
		return json.dumps({"message":"User not found", "status":1, "code":200}), 200
	if action == "status":
		for rec in psutil.net_connections():
			if str(rec.laddr[1]) == port:
				proc = psutil.Process(rec.pid)
				if proc.name() == "node-red":
					return json.dumps({"message":"Instance is running", "status":0, "code":200}), 200
				else:
					return json.dumps({"message":"Instance is not running, PORT occupied by another service: %s" %proc.name(), "status":0, "code":200}) + "\n", 200
		return json.dumps({"message":"Instance is not running", "status":0, "code":200}) + "\n", 200
	elif action == "start":
		if not start_instance(username, port):
			return json.dumps({"message":"Unable to start instance", "status":1, "code":200}), 200
	elif action == "stop":
		if not stop_instance(port):
			return json.dumps({"message":"Unable to stop instance", "status":1, "code":200}), 200
	elif action == "restart":
		if not stop_instance(port):
			return json.dumps({"message":"Unable to stop instance", "status":1, "code":200}), 200
		elif not start_instance(username, port):
			return json.dumps({"message":"Unable to stop instance", "status":1, "code":200}), 200
	return json.dumps({"message":"Instance %s successful" %action, "status":0, "code":200}), 200
	


def start_instance(username, port):
	path = "/root/api/instances/"
	os.chdir(path + username + "/")
	try:
		subprocess.Popen(["nohup", "node-red", "-s", path + username + "/settings.js", "-u", path + username + "/", "-p", str(port)], preexec_fn=os.setpgrp, close_fds=True)
		return True
	except:
		return False


def stop_instance(port):	
	for rec in psutil.net_connections():
		if str(rec.laddr[1]) == str(port):
			try:
				proc = psutil.Process(rec.pid)
				proc.kill()
				return True
			except:
				return False
	return False


if __name__ == "__main__":
	app.run(host = '0.0.0.0', port = 5000, debug=True)
