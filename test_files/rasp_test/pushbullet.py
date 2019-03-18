import requests
import json

import socket
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

API_KEY = 'o.gk8V8J47PGodBeAO0uAUJeZtAoETxJsx' #pushbullet API token

# Send a message to all your registered devices.
def pushMessage(title, body):
	data = {
		'type':'note',
		'title':title,
		'body':body
		}
	resp = requests.post('https://api.pushbullet.com/api/pushes',data=data, auth=(API_KEY,''))

# Test the function:
pushMessage("Parking Found", "Please click the link to access dash camera streaming." + "\n"+ "http://" + IPAddr +":8000")