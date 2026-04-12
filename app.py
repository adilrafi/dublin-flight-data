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

    # Total records
    cur.execute("SELECT COUNT(*) FROM processed_flight_data")
    total_records = cur.fetchone()[0]

    # Peak Windows
    cur.execute("""
        SELECT HOUR(retrieval_time), COUNT(*) 
        FROM processed_flight_data 
        GROUP BY 1 ORDER BY 2 DESC LIMIT 3
    """)
    peaks_raw = cur.fetchall()

    peak_windows = []
    for r in peaks_raw:
        hour = r[0]
        count = r[1]

        perc = round((count / total_records) * 100, 2) if total_records else 0

        peak_windows.append({
            "hour": f"{hour}:00",
            "perc": perc
        })

    # Market Share
    cur.execute("""
        SELECT airline_code, COUNT(*) 
        FROM processed_flight_data 
        WHERE airline_code IS NOT NULL AND airline_code != ''
        GROUP BY 1 ORDER BY 2 DESC LIMIT 5
    """)
    market_raw = cur.fetchall()

    market_share = []
    for r in market_raw:
        airline = r[0]
        count = r[1]

        share = round((count / total_records) * 100, 2)

        market_share.append({
            "airline": airline,
            "share": share
        })

    # Weekend vs Weekday
    cur.execute("""
        SELECT 
            IF(DAYOFWEEK(retrieval_time) IN (1,7), 'Weekend', 'Weekday'),
            COUNT(*)
        FROM processed_flight_data 
        GROUP BY 1
    """)
    day_raw = cur.fetchall()

    traffic_split = {"Weekday": 0, "Weekend": 0}

    for r in day_raw:
        label = r[0]
        count = r[1]

        perc = round((count / total_records) * 100, 1)

        traffic_split[label] = perc

    # Registration
    cur.execute("SELECT COUNT(DISTINCT icao24) FROM processed_flight_data")
    total_unique = cur.fetchone()[0]

    cur.execute("""
        SELECT 
            IF(origin_country = 'Ireland', 'Domestic', 'International'),
            COUNT(DISTINCT icao24)
        FROM processed_flight_data 
        GROUP BY 1
    """)
    reg_raw = cur.fetchall()

    reg_split = {"Domestic": 0, "International": 0}

    for r in reg_raw:
        label = r[0]
        count = r[1]

        perc = round((count / total_unique) * 100, 1) if total_unique else 0

        reg_split[label] = perc

    # Prediction
    cur.execute("""
        SELECT DAYNAME(retrieval_time), COUNT(*) 
        FROM processed_flight_data 
        GROUP BY 1 ORDER BY 2 DESC LIMIT 1
    """)
    pred = cur.fetchone()

    predicted_day = pred[0] if pred else "Analyzing..."

    return jsonify({
        "peak_windows": peak_windows,
        "market_share": market_share,
        "traffic_split": traffic_split,
        "registration_split": reg_split,
        "predicted_day": predicted_day
    })

if __name__ == "__main__":
  app.run(host='0.0.0.0',port='8080') #Run the flask app at port 8080
  # app.run(host='0.0.0.0',port='8080', ssl_context=('cert.pem', 'privkey.pem')) #Run the flask app at port 8080
