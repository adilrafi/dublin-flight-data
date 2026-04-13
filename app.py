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

@app.route("/advanced_stats")
def advanced_stats():
    cur = mysql.cursor()

    # 1. Peak Traffic Windows (Hourly)
    cur.execute("SELECT HOUR(retrieval_time), COUNT(*) FROM processed_flight_data GROUP BY 1 ORDER BY 2 DESC LIMIT 3")
    peak_windows = cur.fetchall()

    # 2. Weekend vs Weekday Traffic
    cur.execute("""
        SELECT IF(DAYOFWEEK(retrieval_time) IN (1, 7), 'Weekend', 'Weekday'), COUNT(*) 
        FROM processed_flight_data GROUP BY 1
    """)
    we_vs_wd = cur.fetchall()

    # 3. Airline Market Share (%)
    cur.execute("""
        SELECT airline_code, (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM processed_flight_data)) 
        FROM processed_flight_data GROUP BY 1 ORDER BY 2 DESC LIMIT 5
    """)
    market_share = cur.fetchall()

    # 4. Growth Trend (Day-by-Day Change)
    cur.execute("""
        SELECT DATE(retrieval_time), COUNT(*) 
        FROM processed_flight_data GROUP BY 1 ORDER BY 1 ASC
    """)
    growth_data = cur.fetchall()

    # 5. International vs Domestic (Based on origin_country field)
    # If country is Ireland, it's domestic; otherwise international [7]
    cur.execute("""
        SELECT IF(origin_country = 'Ireland', 'Domestic', 'International'), COUNT(*) 
        FROM processed_flight_data GROUP BY 1
    """)
    intl_vs_dom = cur.fetchall()

    # 6. Predict Next Busiest Day (Simple Model based on historical mode)
    cur.execute("SELECT DAYNAME(retrieval_time) FROM processed_flight_data GROUP BY 1 ORDER BY COUNT(*) DESC LIMIT 1")
    prediction = cur.fetchone()

    # Formatting into a clean human-readable JSON
    stats = {
        "peaks": [{"hour": f"{r}:00", "count": r[1]} for r in peak_windows],
        "work_split": {r: r[1] for r in we_vs_wd},
        "market": [{"name": r, "share": round(r[1], 2)} for r in market_share],
        "trends": [{"date": str(r), "count": r[1]} for r in growth_data],
        "origin_split": {r: r[1] for r in intl_vs_dom},
        "next_busy_prediction": prediction if prediction else "Analyzing..."
    }
    return json.dumps(stats)

if __name__ == "__main__":
  app.run(host='0.0.0.0',port='8080') #Run the flask app at port 8080
  # app.run(host='0.0.0.0',port='8080', ssl_context=('cert.pem', 'privkey.pem')) #Run the flask app at port 8080
