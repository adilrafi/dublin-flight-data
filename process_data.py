import mysql.connector
import pandas as pd

# Database Connection
db_config = {
    'user': 'web',
    'password': 'webPass',
    'host': '127.0.0.1',
    'database': 'student'
}

def process_pipeline():
    try:
        conn = mysql.connector.connect(**db_config)
        
        # Extraction: Get raw data from the first table
        query = "SELECT icao24, callsign, origin_country, velocity, vertical_rate, on_ground, retrieval_time FROM flight_data"
        df = pd.read_sql(query, conn)
        
        if df.empty:
            print("No data found to process.")
            return

        # Data Cleaning: Handle missing values found in OpenSky data
        df['velocity'] = df['velocity'].fillna(0)
        df['vertical_rate'] = df['vertical_rate'].fillna(0)
        df['callsign'] = df['callsign'].fillna('UNKNOWN').str.strip()

        # Feature Extraction & Transformations
        
        # Feature: Extract Airline Code (First 3 chars of callsign)
        df['airline_code'] = df['callsign'].str[:3]
        
        # Feature: Categorize Flight Phase (Climbing, Descending, Level)
        def determine_phase(row):
            if row['on_ground']: return 'Grounded'
            if row['vertical_rate'] > 0.5: return 'Climbing'
            if row['vertical_rate'] < -0.5: return 'Descending'
            return 'Level'
        df['flight_phase'] = df.apply(determine_phase, axis=1)

        # Feature: Local vs International Registration
        df['is_local_fleet'] = df['origin_country'] == 'Ireland'

        # Feature: Temporal Analysis (Hour and Day for Peak Hour analysis)
        df['hour_of_day'] = df['retrieval_time'].dt.hour
        df['day_of_week'] = df['retrieval_time'].dt.day_name()

        # Loading: Save to the new appropriate database table
        cursor = conn.cursor()
        for _, row in df.iterrows():
            insert_query = """
            INSERT IGNORE INTO processed_flight_data 
            (icao24, airline_code, origin_country, flight_phase, is_local_fleet, velocity, hour_of_day, day_of_week, retrieval_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                row['icao24'], row['airline_code'], row['origin_country'], 
                row['flight_phase'], row['is_local_fleet'], row['velocity'],
                row['hour_of_day'], row['day_of_week'], row['retrieval_time']
            ))
        
        conn.commit()
        print(f"Successfully processed {len(df)} records.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    process_pipeline()
