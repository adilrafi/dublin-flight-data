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
    res = cur.fetchone()
    total_records = res if res and res > 0 else 0

    # 1. Peak Traffic Windows
    cur.execute("SELECT HOUR(retrieval_time), COUNT(*) FROM processed_flight_data GROUP BY 1 ORDER BY 2 DESC LIMIT 3")
    peaks_raw = cur.fetchall()
    peak_windows = [{"hour": f"{row}:00", "perc": round((row[1]/total_records)*100, 2)} for row in peaks_raw] if total_records > 0 else []

    # 2. Airline Market Share
    cur.execute("SELECT airline_code, COUNT(*) FROM processed_flight_data WHERE airline_code != '' GROUP BY 1 ORDER BY 2 DESC LIMIT 5")
    market_raw = cur.fetchall()
    market_share = [{"airline": r, "share": round((r[1]/total_records)*100, 2)} for r in market_raw] if total_records > 0 else []

    # 3. Day Density
    cur.execute("SELECT IF(DAYOFWEEK(retrieval_time) IN (1, 7), 'Weekend', 'Weekday'), COUNT(*) FROM processed_flight_data GROUP BY 1")
    day_raw = cur.fetchall()
    traffic_split = {row: round((row[1]/total_records)*100, 1) for row in day_raw} if total_records > 0 else {"Weekday": 0, "Weekend": 0}

    # 4. Registration
    cur.execute("SELECT COUNT(DISTINCT icao24) FROM processed_flight_data")
    res_u = cur.fetchone()
    total_unique = res_u if res_u and res_u > 0 else 0
    cur.execute("SELECT IF(origin_country = 'Ireland', 'Domestic', 'International'), COUNT(DISTINCT icao24) FROM processed_flight_data GROUP BY 1")
    reg_raw = cur.fetchall()
    registration_split = {row: round((row[1]/total_unique)*100, 1) for row in reg_raw} if total_unique > 0 else {"Domestic": 0, "International": 0}

    # 5. Prediction
    cur.execute("SELECT DAYNAME(retrieval_time) FROM processed_flight_data GROUP BY 1 ORDER BY COUNT(*) DESC LIMIT 1")
    pred_res = cur.fetchone()
    predicted_day = pred_res if pred_res else "Analyzing..."

    return jsonify({
        "peak_windows": peak_windows,
        "market_share": market_share,
        "traffic_split": traffic_split,
        "registration_split": registration_split,
        "predicted_day": predicted_day
    })  
if __name__ == "__main__":
  app.run(host='0.0.0.0',port='8080') #Run the flask app at port 8080
  # app.run(host='0.0.0.0',port='8080', ssl_context=('cert.pem', 'privkey.pem')) #Run the flask app at port 8080
