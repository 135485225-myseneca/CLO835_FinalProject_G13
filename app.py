from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# Initialize Flask app
app = Flask(__name__)

# Retrieve values from ConfigMap
bucket_name = os.environ.get('bucket') 
bg_image_url = os.environ.get('bgimg')
group_name = os.environ.get('grpname')
group_slogan = os.environ.get('groupslogan')

# Retrieve AWS credentials from K8s secrets
aws_access_key = os.environ.get('AWS_ACCESS_KEY')
aws_secret_key = os.environ.get('AWS_SECRET_KEY')

# Retrieve MySQL credentials from K8s secrets
DBHOST = os.environ.get("DBHOST")
DBUSER = os.environ.get("DBUSER")
DBPWD = os.environ.get("DBPWD")
DATABASE = os.environ.get("DATABASE")
DBPORT = int(os.environ.get("DBPORT", '3306'))

# Specify local path to store the downloaded image
BACKGROUND_IMAGE_PATH = 'static/background.jpeg'

# Create a connection to the MySQL database
db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE
)

# Download the background image before each request
# decorator to allow to define a function that will be executed before each request to Flask application
@app.before_request
def download_background_image():
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

    try:
        # Parse the S3 URL to get the bucket and key
        key = bg_image_url.split(f'https://{bucket_name}.s3.amazonaws.com/')[1]

        # Download the file from S3 and save it locally
        s3.download_file(bucket_name, key, BACKGROUND_IMAGE_PATH)
        print(f"Image downloaded successfully to {BACKGROUND_IMAGE_PATH}")

    except (NoCredentialsError, ClientError) as e:
        print(f"An error occurred while downloading the image: {e}")

# Define routes for your application
@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('addemp.html', group_name=group_name, group_slogan=group_slogan,
                           background_image=BACKGROUND_IMAGE_PATH)

@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html', group_name=group_name, group_slogan=group_slogan,
                           background_image=BACKGROUND_IMAGE_PATH)

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
        emp_name = f"{first_name} {last_name}"
    finally:
        cursor.close()

    print("All modifications done...")
    return render_template('addempoutput.html', name=emp_name, group_name=group_name, group_slogan=group_slogan,
                           background_image=BACKGROUND_IMAGE_PATH)

   # GetEmp route
@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", group_name=group_name, group_slogan=group_slogan,
                           background_image=BACKGROUND_IMAGE_PATH)

# FetchData route
@app.route("/fetchdata", methods=['GET', 'POST'])
def FetchData():
    emp_id = request.form['emp_id']
    output = {}

    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location from employee where emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()
        
        if result:
            output["emp_id"] = result[0]
            output["first_name"] = result[1]
            output["last_name"] = result[2]
            output["primary_skills"] = result[3]
            output["location"] = result[4]
        else:
            print(f"No employee found with ID: {emp_id}")

    except Exception as e:
        print(e)
    finally:
        cursor.close()

    return render_template("getempoutput.html", id=output.get("emp_id"), fname=output.get("first_name"),
                           lname=output.get("last_name"), interest=output.get("primary_skills"), 
                           location=output.get("location"), group_name=group_name, group_slogan=group_slogan,
                           background_image=BACKGROUND_IMAGE_PATH)

if __name__ == '__main__':
    # Run Flask app on port 81
    app.run(host='0.0.0.0', port=81, debug=True)
