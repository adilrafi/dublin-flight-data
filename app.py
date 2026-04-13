from flask import Flask, jsonify
from flask import render_template
from flask import request
import mysql.connector
from flask_cors import CORS
import json
mysql = mysql.connector.connect(user='web', password='webPass',
  host='127.0.0.1',
  database='student')

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})
app = Flask(__name__)
CORS(app)
# My SQL Instance configurations
# Change the HOST IP and Password to match your instance configurations

@app.route("/test")#URL leading to method
def test(): # Name of the method
 return("Hello World!<BR/>THIS IS ANOTHER TEST!") #indent this line

@app.route("/yest")#URL leading to method
def yest(): # Name of the method
 return("Hello World!<BR/>THIS IS YET ANOTHER TEST!") #indent this line

@app.route("/add", methods=['GET', 'POST']) #Add Student
def add():
  if request.method == 'POST':
    name = request.form['name']
    email = request.form['email']
    print(name,email)
    cur = mysql.cursor() #create a connection to the SQL instance
    s='''INSERT INTO students(studentName, email) VALUES(%s,%s);'''
    app.logger.info(s)
    cur.execute(s,(name,email))
    mysql.commit()
  else:
    return render_template('add.html')

  return '{"Result":"Success"}'
@app.route("/") #Default - Show Data
def hello(): # Name of the method
  cur = mysql.cursor() #create a connection to the SQL instance
  cur.execute('''SELECT * FROM students''') # execute an SQL statment
  rv = cur.fetchall() #Retreive all rows returend by the SQL statment
  Results=[]
  for row in rv: #Format the Output Results and add to return string
    Result={}
    Result['Name']=row[0].replace('\n',' ')
    Result['Email']=row[1]
    Result['ID']=row[2]
    Results.append(Result)
  response={'Results':Results, 'count':len(Results)}
  ret=app.response_class(
    response=json.dumps(response),
    status=200,
    mimetype='application/json'
  )
  return ret #Return the data in a string format

@app.route("/flight_stats")
def flight_stats():
    cur = mysql.cursor()

    # 1. Total Unique Aircraft (The Denominator)
    # This ensures we count each airplane once, regardless of how many times it was seen.
    cur.execute("SELECT COUNT(DISTINCT icao24) FROM processed_flight_data")
    total_unique = cur.fetchone()

    # 2. Peak Traffic Windows (% of total unique fleet)
    cur.execute("""
        SELECT HOUR(retrieval_time) as hr, COUNT(DISTINCT icao24) as volume 
        FROM processed_flight_data 
        GROUP BY hr ORDER BY volume DESC LIMIT 3
    """)
    peaks_raw = cur.fetchall()
    peak_windows = []
    for row in peaks_raw:
        # Transformation: What % of the total unique fleet was active during this hour?
        percentage = round((row[1] / total_unique) * 100, 2) if total_unique > 0 else 0
        peak_windows.append({"hour": f"{row}:00", "percentage": percentage})

    # 3. Fleet Registration Split (Domestic vs International)
    # Registration is based on the 'origin_country' field from the OpenSky API [2, 3]
    cur.execute("""
        SELECT IF(origin_country = 'Ireland', 'Domestic', 'International') as reg_type, 
               COUNT(DISTINCT icao24) as unique_count 
        FROM processed_flight_data GROUP BY 1
    """)
    reg_raw = cur.fetchall()
    registration_split = {"Domestic": 0, "International": 0}
    for row in reg_raw:
        # We calculate the percentage of the unique fleet for each category
        percentage = round((row[1] / total_unique) * 100, 1) if total_unique > 0 else 0
        registration_split[row] = percentage

    # 4. Congestion Prediction Model
    # Simple mode-based prediction for the next busiest day [4]
    cur.execute("""
        SELECT DAYNAME(retrieval_time) 
        FROM processed_flight_data 
        GROUP BY 1 ORDER BY COUNT(DISTINCT icao24) DESC LIMIT 1
    """)
    prediction_row = cur.fetchone()
    prediction = prediction_row if prediction_row else "Analyzing..."

    # Consolidating into the final JSON payload for our integration test
    analytics_payload = {
        "peak_windows": peak_windows,
        "registration_split": registration_split,
        "predicted_busy_day": prediction
    }
    
    return json.dumps(analytics_payload)

if __name__ == "__main__":
  app.run(host='0.0.0.0',port='8080') #Run the flask app at port 8080
  # app.run(host='0.0.0.0',port='8080', ssl_context=('cert.pem', 'privkey.pem')) #Run the flask app at port 8080
