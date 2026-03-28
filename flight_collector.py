import requests
import mysql.connector
from datetime import datetime

# -------------------------------
# OpenSky API Credentials
# -------------------------------
CLIENT_ID = "adil793@hotmail.com-api-client"
# REPLACE THE SECRET BELOW
CLIENT_SECRET = "wjMNkckY4ISqWfiA5NWJaw8mGXEMPbC1"

# -------------------------------
# Get OAuth2 Token
# -------------------------------
token_url = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
token_data = {
    "grant_type": "client_credentials", 
    "client_id": CLIENT_ID, 
    "client_secret": CLIENT_SECRET}

token_response = requests.post(token_url, data=token_data)
if token_response.status_code != 200:
    print("Error getting token:", token_response.status_code)
    exit()

access_token = token_response.json()['access_token']
headers = {"Authorization": f"Bearer {access_token}"}

# -------------------------------
# Dublin Airport Bounding Box & Request Aircraft Data
# -------------------------------
LAMIN, LAMAX = 53.35, 53.50
LOMIN, LOMAX = -6.40, -6.15
url = f"https://opensky-network.org/api/states/all?lamin={LAMIN}&lomin={LOMIN}&lamax={LAMAX}&lomax={LOMAX}"

response = requests.get(url, headers=headers)
if response.status_code != 200:
    print(f"Error retrieving data: {response.status_code}")
    exit()

data = response.json()
states = data.get("states", [])

# -------------------------------
# Connect to MariaDB
# -------------------------------
db = mysql.connector.connect(
    user='web', 
    password='webPass', 
    host='127.0.0.1', 
    database='student'
)
cursor = db.cursor()

# -------------------------------
# Save Data into Database
# -------------------------------
retrieval_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if states:
    for s in states:
        # We add the retrieval_time at the end of each flight record
        s.append(retrieval_time)
        
        # Prepare the SQL command
        sql = """INSERT INTO flight_data (
                    icao24, callsign, origin_country, time_position, last_contact, 
                    longitude, latitude, baro_altitude, on_ground, velocity, 
                    true_track, vertical_rate, sensors, geo_altitude, squawk, 
                    spi, position_source, retrieval_time
                 ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        # Insert the row (the state vector 's')
        cursor.execute(sql, tuple(s))
    
    db.commit()
    print(f"Successfully saved {len(states)} flight records to the database.")
else:
    print("No aircraft found in the selected area.")

# Clean up
cursor.close()
db.close()
