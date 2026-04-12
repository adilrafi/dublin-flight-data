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

    # Total records for volume calculation
    cur.execute("SELECT COUNT(*) FROM processed_flight_data")
    total_records = cur.fetchone()

    # Peak Traffic Windows (% of total daily volume)
    cur.execute("""
        SELECT HOUR(retrieval_time), COUNT(*) 
        FROM processed_flight_data 
        GROUP BY 1 ORDER BY 2 DESC LIMIT 3
    """)
    peaks_raw = cur.fetchall()
    peak_windows = [{"hour": f"{r}:00", "perc": round((r[3]/total_records)*100, 2)} for r in peaks_raw]

    # Airline Market Share (% of total volume)
    cur.execute("""
        SELECT airline_code, COUNT(*) 
        FROM processed_flight_data 
        WHERE airline_code IS NOT NULL AND airline_code != ''
        GROUP BY 1 ORDER BY 2 DESC LIMIT 5
    """)
    market_raw = cur.fetchall()
    market_share = [{"airline": r, "share": round((r[3]/total_records)*100, 2)} for r in market_raw]

    # Day Density (Weekend vs Weekday % of volume)
    cur.execute("""
        SELECT IF(DAYOFWEEK(retrieval_time) IN (1, 7), 'Weekend', 'Weekday'), COUNT(*) 
        FROM processed_flight_data GROUP BY 1
    """)
    day_raw = cur.fetchall()
    traffic_split = {r: round((r[3]/total_records)*100, 1) for r in day_raw}

    # Registration (Unique Aircraft via icao24)
    # Registration is domestic if origin_country is 'Ireland' [10]
    cur.execute("SELECT COUNT(DISTINCT icao24) FROM processed_flight_data")
    total_unique = cur.fetchone()

    cur.execute("""
        SELECT IF(origin_country = 'Ireland', 'Domestic', 'International'), COUNT(DISTINCT icao24) 
        FROM processed_flight_data GROUP BY 1
    """)
    reg_raw = cur.fetchall()
    reg_split = {r: round((r[3]/total_unique)*100, 1) for r in reg_raw}

    # Prediction (Next busiest day based on historical frequency)
    cur.execute("SELECT DAYNAME(retrieval_time) FROM processed_flight_data GROUP BY 1 ORDER BY COUNT(*) DESC LIMIT 1")
    prediction = cur.fetchone()

    return jsonify({
        "peak_windows": peak_windows,
        "market_share": market_share,
        "traffic_split": traffic_split,
        "registration_split": reg_split,
        "predicted_day": prediction
    })


if __name__ == "__main__":
  app.run(host='0.0.0.0',port='8080') #Run the flask app at port 8080
  # app.run(host='0.0.0.0',port='8080', ssl_context=('cert.pem', 'privkey.pem')) #Run the flask app at port 8080
