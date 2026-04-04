USE student;

CREATE TABLE processed_flight_data (
    icao24 VARCHAR(50),
    airline_code VARCHAR(10),
    origin_country VARCHAR(100),
    flight_phase VARCHAR(50),
    is_local_fleet BOOLEAN,
    velocity FLOAT,
    hour_of_day INT,
    day_of_week VARCHAR(20),
    retrieval_time DATETIME,
    PRIMARY KEY (icao24, retrieval_time)
);
