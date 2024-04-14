from flask import Flask, render_template, request
from pymysql import connections
import os
import random
import boto3
from botocore.exceptions import NoCredentialsError

# Initialize Flask app
app = Flask(__name__)

# AWS S3 configuration
AWS_BUCKET_NAME = 'project-clo835'
AWS_REGION_NAME = 'us-east-1'
DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER") or "root"
DBPWD = os.environ.get("DBPWD") or "password"
DATABASE = os.environ.get("DATABASE") or "employees"
DBPORT = int(os.environ.get("DBPORT"))

# Create a connection to the MySQL database
db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD, 
    db=DATABASE
)

# Initialize AWS S3 client
s3 = boto3.client('s3', region_name=AWS_REGION_NAME)

# Specify local path to store the downloaded image
BACKGROUND_IMAGE_PATH = 'static/background.jpeg'

# Download a random image from S3 bucket
def download_background_image():
        s3.download_file(AWS_BUCKET_NAME, random_image_key, BACKGROUND_IMAGE_PATH)

# Route for home page
@app.route("/", methods=['GET', 'POST'])
def home():
    download_background_image()  # Download background image on each request to ensure freshness
    return render_template('addemp.html', background_image=BACKGROUND_IMAGE_PATH)

# Route for about page
@app.route("/about", methods=['GET','POST'])
def about():
    download_background_image()  # Download background image on each request to ensure freshness
    return render_template('about.html', background_image=BACKGROUND_IMAGE_PATH)

# AddEmp route
@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']
  
    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
    finally:
        cursor.close()

    print("All modifications done...")
    return render_template('addempoutput.html', name=emp_name, background_image=BACKGROUND_IMAGE_PATH)

# GetEmp route
@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", background_image=BACKGROUND_IMAGE_PATH)

# FetchData route
@app.route("/fetchdata", methods=['GET','POST'])
def FetchData():
    emp_id = request.form['emp_id']
    output = {}

    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location from employee where emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id))
        result = cursor.fetchone()
        
         # Add No Employee found form
        output["emp_id"] = result[0]
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["primary_skills"] = result[3]
        output["location"] = result[4]
        
    except Exception as e:
        print(e)
    finally:
        cursor.close()

    return render_template("getempoutput.html", id=output["emp_id"], fname=output["first_name"],lname=output["last_name"], interest=output["primary_skills"], location=output["location"], background_image=BACKGROUND_IMAGE_PATH)

if __name__ == '__main__':
    # Run Flask app
    app.run(host='0.0.0.0', port=8080, debug=True)
