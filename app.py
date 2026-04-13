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

    # First, get the total count of all records for percentage calculation
    cur.execute("SELECT COUNT(*) FROM processed_flight_data")
    total_records = cur.fetchone() # Using  to extract the value from the tuple

    # 1. Peak Traffic Windows (Transformed to % of total traffic)
    # We fetch the top 3 busiest hours
    cur.execute("""
        SELECT HOUR(retrieval_time) as hr, COUNT(*) as volume 
        FROM processed_flight_data 
        GROUP BY hr ORDER BY volume DESC LIMIT 3
    """)
    peaks_raw = cur.fetchall()
    
    # Transformation: Calculate what percentage of the day's traffic happens in these hours
    peak_windows = []
    for row in peaks_raw:
        hour_label = f"{row}:00"
        # Calculation: (Hourly Count / Total Records) * 100
        percentage = round((row[1] / total_records) * 100, 2) if total_records > 0 else 0
        peak_windows.append({"hour": hour_label, "percentage": percentage})

    # 2. Airline Market Share (%)
    # Calculates the percentage of total traffic for the top 5 carriers
    cur.execute("""
        SELECT airline_code, (COUNT(*) * 100.0 / %s) 
        FROM processed_flight_data 
        GROUP BY 1 ORDER BY 2 DESC LIMIT 5
    """, (total_records,))
    market_raw = cur.fetchall()
    market_share = [{"airline": r, "share": round(r[1], 2)} for r in market_raw]

    # 3. Congestion Prediction Model
    # Identifies the next busiest day based on historical frequency
    cur.execute("""
        SELECT DAYNAME(retrieval_time) 
        FROM processed_flight_data 
        GROUP BY 1 ORDER BY COUNT(*) DESC LIMIT 1
    """)
    prediction_row = cur.fetchone()
    prediction = prediction_row if prediction_row else "Analyzing..."

    # Consolidating into a clean JSON payload for the integration test [1]
    analytics_payload = {
        "peak_windows": peak_windows,
        "market_share": market_share,
        "predicted_busy_day": prediction
    }
    
    return json.dumps(analytics_payload)
  
if __name__ == "__main__":
  app.run(host='0.0.0.0',port='8080') #Run the flask app at port 8080
  # app.run(host='0.0.0.0',port='8080', ssl_context=('cert.pem', 'privkey.pem')) #Run the flask app at port 8080
