#hello.py
from flask import Flask
app = Flask(__name__)
@app.route("/")#URL leading to method
def hello(): # Name of the method
 return("Hello World!") #indent this line
if __name__ == "__main__":
 app.run(host='0.0.0.0', port='8080') # indent this line

 ====================

#Click commit to main

#Click code 

#Copy the .git link

#git clone <repo link> # it will say cloning into <X>

cd <X>

 ../bin/pip3 install flask
 ../bin/python3 hello.py
#ensure port 8080 is open on portal.azure.com or Google VPC Firewall

then in Chrome, visit http://<IP>:8080

you should see 

Hello World!

#Returning to terminal, run:

#Let's get Flask running on https:
#run
sudo apt -y install apache2
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
#make sure you have configured you DNS (hostname) on Azure
sudo certbot --apache
sudo cp /etc/letsencrypt/live/<hostname>/cert.pem .
sudo cp /etc/letsencrypt/live/<hostname>/privkey.pem .
sudo chown `whoami` *.pem
#edit hello.py on GitHub 
change the last line to:

app.run(host='0.0.0.0',port='8080', ssl_context=('cert.pem', 'privkey.pem')) #Run the flask app at port 8080

run
python3 hello.py