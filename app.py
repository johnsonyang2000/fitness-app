from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import tensorflow as tf
import tensorflow_hub as hub

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    bmr = db.Column(db.Float, nullable=False)

class DailyWeight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    weight = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    bmr = db.Column(db.Float, nullable=False)
    user = db.relationship('User', backref=db.backref('daily_weights', lazy=True))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    exercise = db.Column(db.String(150), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('bmi'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            return redirect(url_for('task_manager'))
        else:
            flash('Invalid credentials', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/task_manager', methods=['GET', 'POST'])
def task_manager():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username = session['username']).first()

    if request.method == 'POST':
        exercise = request.form['exercise']
        sets = request.form['sets']
        reps = request.form['reps']
        new_task = Task(user_id=user.id, exercise = exercise, sets=sets, reps = reps)
        db.session.add(new_task)
        db.session.commit()
        flash('Exercise added successfully!', 'sucess')
        return redirect('task_manager')
    tasks = Task.query.filter_by(user_id=user.id).all()
    return render_template('task_manager.html', tasks = tasks)

@app.route('/delete_task/<int:task_id>', methods = ['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    return redirect(url_for('task_manager'))

@app.route('/complete_task/<int:task_id>', methods = ['POST'])
def complete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        task.completed = not task.completed
        db.session.commit()
    return redirect(url_for('task_manager'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        retype_password = request.form['retype_password']
        date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d')
        gender = request.form['gender']
        weight = float(request.form['weight'])
        height = float(request.form['height'])

        if password != retype_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))

        # Calculate age
        today = datetime.today()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))

        # Calculate BMI
        height_in_meters = height / 100  # convert cm to meters
        bmi = round(weight / (height_in_meters ** 2), 2)

        # Calculate BMR using Revised Harris-Benedict Equation
        if gender == 'Male':
            bmr = round(13.397 * weight + 4.799 * height + 5.677 * age + 88.362, 2)
        else:
            bmr = round(9.247 * weight + 3.098 * height + 4.330 * age + 447.593, 2)

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user = User(username=username, password=hashed_password, date_of_birth=date_of_birth, age=age, gender=gender,
                        weight=weight, height=height, bmi=bmi, bmr=bmr)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/bmi')
def bmi():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        latest_entry = DailyWeight.query.filter_by(user_id=user.id).order_by(DailyWeight.date.desc()).first()
        daily_entries = DailyWeight.query.filter_by(user_id=user.id).order_by(DailyWeight.date.asc()).all()
        
        # Format dates as strings
        daily_entries_data = [{
            'date': entry.date.strftime('%Y-%m-%d'),
            'weight': entry.weight,
            'bmi': entry.bmi,
            'bmr': entry.bmr
        } for entry in daily_entries]
        
        return render_template('bmi.html', user=user, latest_entry=latest_entry, daily_entries=daily_entries_data)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/add_weight', methods=['GET', 'POST'])
def add_weight():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if request.method == 'POST':
            weight = request.form['weight']
            try:
                weight = float(weight)
            except ValueError:
                flash('Please enter a valid weight.', 'error')
                return redirect(url_for('add_weight'))

            # Ensure the weight is within a reasonable range
            if not (30 <= weight <= 300):
                flash('Please enter a weight between 30kg and 300kg.', 'error')
                return redirect(url_for('add_weight'))

            # Check if the user has already entered weight for today
            today = datetime.today().date()
            existing_entry = DailyWeight.query.filter_by(user_id=user.id, date=today).first()
            if existing_entry:
                flash('You have already recorded your weight for today.', 'error')
                return redirect(url_for('add_weight'))

            # Calculate BMI
            height_in_meters = user.height / 100  # convert cm to meters
            bmi = round(weight / (height_in_meters ** 2), 2)

            # Calculate BMR using Revised Harris-Benedict Equation
            if user.gender == 'Male':
                bmr = round(13.397 * weight + 4.799 * user.height + 5.677 * user.age + 88.362, 2)
            else:
                bmr = round(9.247 * weight + 3.098 * user.height + 4.330 * user.age + 447.593, 2)

            # Add new weight entry
            new_entry = DailyWeight(user_id=user.id, weight=weight, date=today, bmi=bmi, bmr=bmr)
            db.session.add(new_entry)
            db.session.commit()
            flash('Weight recorded successfully!', 'success')
            return redirect(url_for('bmi'))

        return render_template('add_weight.html')
    return redirect(url_for('login'))

embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
def generate_workout(exercise_type, workout_duration, intensity):
    # Define some basic workouts
    workouts = {
        "cardio": {
            "low": ["walking", "light jogging"],
            "medium": ["jogging", "cycling"],
            "high": ["running", "HIIT"]
        },
        "strength": {
            "low": ["bodyweight exercises", "light weights"],
            "medium": ["moderate weights", "resistance bands"],
            "high": ["heavy weights", "advanced bodyweight exercises"]
        },
        "flexibility": {
            "low": ["light stretching", "basic yoga"],
            "medium": ["yoga", "pilates"],
            "high": ["advanced yoga", "dynamic stretching"]
        }
    }

    # Select workouts based on the input
    selected_workouts = workouts.get(exercise_type.lower(), {}).get(intensity.lower(), [])
    
    # Format the recommendation
    if selected_workouts:
        recommendation = f"For a {workout_duration}-minute {exercise_type.lower()} workout at {intensity.lower()} intensity, you can try: {', '.join(selected_workouts)}."
    else:
        recommendation = "No workouts available for the selected options."

    return recommendation

@app.route('/generate_exercise', methods=['GET', 'POST'])
def generate_exercise():
    if request.method == 'POST':
        exercise_type = request.form['exercise_type']
        workout_duration = request.form['workout_duration']
        intensity = request.form['intensity']
        
        workout = generate_workout(exercise_type, workout_duration, intensity)
        return render_template('generate_exercise.html', workout=workout)
    return render_template('generate_exercise.html', workout=None)




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
