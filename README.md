Project Overview: Dublin Air Traffic Intelligence System

This project involved the development of a complete Data Acquisition and Preprocessing Pipeline designed to monitor and analyse flight patterns at Dublin Airport. The system automates the collection of real-time aircraft state vectors, transforms them into actionable insights, and presents them via a live web-based dashboard.
Technology Stack & Implementation

•	OpenSky Network API: Used as the primary data source for acquiring real-time aircraft state vectors for the Dublin Airport bounding box.

•	Flask Framework: Employed to develop the backend system, including the implementation of the API routes (/flight_stats, /add, /) and the serving of the frontend templates.
•	MariaDB: Utilized as the relational database management system for storing and managing the acquired flight data and student records.
•	Pandas: Integrated for data preprocessing, cleaning, and transformation of the raw API responses into structured dataframes for analysis.
•	mysql-connector-python: Used to provide the critical connection between the Python/Flask backend and the MariaDB SQL instance.
•	Requests Library: Used to facilitate the OAuth2 token generation and subsequent HTTP GET requests to the OpenSky Network API.
•	Flask-CORS: Integrated to handle Cross-Origin Resource Sharing, allowing the frontend to interact securely with the backend API.
•	Ubuntu VM (Azure/Google Cloud): Hosted the entire application environment to ensure persistent data collection and 24/7 API availability.
•	Automated Task Scheduling (Crontab): Implemented system-level cron jobs to automate the 15-minute data collection and 30-minute processing cycles, ensuring the database remains current without manual intervention.
•	Responsive Web Dashboard: Developed a custom frontend using HTML, CSS, and JavaScript that performs asynchronous fetch requests to the Flask API to display real-time traffic intelligence and predictions.

Key Features & Transformations

•	Peak Traffic Analysis: SQL-driven logic to identify the busiest hours for Dublin Airport traffic.
•	Market Share Intelligence: Quantitative analysis of airline dominance based on active aircraft counts.
•	Operational Density: Dynamic calculation of traffic splits between weekdays and weekends.
•	Fleet Origin Tracking: Differentiation between domestic (Irish-registered) and international aircraft based on origin_country metadata.
•	Predictive Insights: Implementation of a basic model to estimate the next busiest day based on historical retrieval patterns.


Guide lines to run this project

1. Environment Setup
The project is designed to run on an Ubuntu Virtual Machine (Azure or Google Cloud instance).
•	Update System: Run sudo apt update && sudo apt -y upgrade.
•	Install Dependencies: Install the necessary Python and system packages:
•	Virtual Environment: Create and activate a virtual environment to manage dependencies:
2. Database Configuration
This project uses MariaDB to store both administrative records and processed flight data.
•	Initialize Database: Access the MariaDB console using sudo mysql and execute the following:
•	Install Connectors: Install the required Python-SQL bridge:
3. Data Pipeline Automation
The system uses Crontab to ensure continuous data acquisition from the OpenSky Network API without manual intervention.
•	Configure Cron Jobs: Open the crontab editor (crontab -e) and add the following tasks:
o	Data Collection: Set flight_collector.py to run every 15 minutes.
o	Data Processing: Set process_data.py to run every 30 minutes.
o	Example: */15 * * * * /home/<user>/venv/bin/python3 /home/<user>/Programming-Data-Analysis/flight_collector.py.
4. Launching the Backend API
•	Clone the Repository: Use git clone <repo_link> to pull the source code.
•	Run Flask: Start the backend server on port 8080:
•	Firewall Configuration: Ensure port 8080 is open in your Cloud Provider’s network security group/firewall settings.
5. Accessing the Dashboard
•	Frontend Deployment: Place the index.html file in the web server directory (e.g., /var/www/html/).
•	Integration: Ensure the fetch URL in the JavaScript section of index.html points to your VM's public IP address at port 8080.
•	View Results: Open your browser and navigate to http://<Your-VM-IP>/index.html to view the live Dublin Air Traffic Intelligence Dashboard


