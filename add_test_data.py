from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

# Create and configure the Flask app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance/users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the DailyWeight model to match your existing table
class DailyWeight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    bmr = db.Column(db.Float, nullable=False)

# Replace 'user_id' with the actual user ID you want to add the data for
user_id = 1

# Starting date for the new data entries
start_date = datetime.now()

# List of new weight entries for 10 days
new_weights = [85.0, 84.5, 84.0, 83.5, 83.0, 82.5, 82.0, 81.5, 81.0, 80.5]

# Function to calculate BMI
def calculate_bmi(weight, height):
    return round(weight / ((height / 100) ** 2), 2)

# Function to calculate BMR (using Mifflin-St Jeor Equation for demonstration)
def calculate_bmr(weight, height, age, gender):
    if gender == 'Male':
        return round(10 * weight + 6.25 * height - 5 * age + 5, 2)
    else:
        return round(10 * weight + 6.25 * height - 5 * age - 161, 2)

# User details (replace these with actual user details)
height = 188  # in cm
age = 24  # in years
gender = 'Male'

# Adding new entries to the database
with app.app_context():
    try:
        for i, weight in enumerate(new_weights):
            date = start_date - timedelta(days=i)
            bmi = calculate_bmi(weight, height)
            bmr = calculate_bmr(weight, height, age, gender)
            new_entry = DailyWeight(user_id=user_id, date=date, weight=weight, bmi=bmi, bmr=bmr)
            db.session.add(new_entry)
            print(f"Added entry for date: {date}, weight: {weight}, bmi: {bmi}, bmr: {bmr}")  # Debug info

        db.session.commit()
        print("Test data added successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.session.close()
