from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Add this line after creating the Flask app
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)
login_manager = LoginManager(app)

# New models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    weight = db.Column(db.Float)
    desired_weight = db.Column(db.Float)  # Add this line

class CalorieEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    calories = db.Column(db.Float, nullable=False)
    image_path = db.Column(db.String(255))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# New routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    new_user = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({'message': 'Logged in successfully'}), 200
    
    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/update_weight', methods=['POST'])
@login_required
def update_weight():
    data = request.get_json()
    new_weight = data.get('weight')
    
    if new_weight is None:
        return jsonify({'error': 'Weight not provided'}), 400
    
    current_user.weight = new_weight
    db.session.commit()
    
    return jsonify({'message': 'Weight updated successfully'}), 200

@app.route('/api/add_calorie_entry', methods=['POST'])
@login_required
def add_calorie_entry():
    calories = request.form.get('calories')
    image = request.files.get('image')
    
    if not calories:
        return jsonify({'error': 'Calories not provided'}), 400
    
    entry = CalorieEntry(user_id=current_user.id, calories=float(calories))
    
    if image:
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        entry.image_path = image_path
    
    db.session.add(entry)
    db.session.commit()
    
    return jsonify({'message': 'Calorie entry added successfully'}), 201

@app.route('/api/calorie_history', methods=['GET'])
@login_required
def get_calorie_history():
    entries = CalorieEntry.query.filter_by(user_id=current_user.id).order_by(CalorieEntry.date.desc()).all()
    history = [{'date': entry.date, 'calories': entry.calories, 'image_path': entry.image_path} for entry in entries]
    return jsonify(history), 200

@app.route('/api/calorie', methods=['POST'])
def calculate_calories():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        items = data['items']
        total_calories = 0

        # Loop through each item to calculate total calories
        for item in items:
            name = item.get('name', 'Unknown')
            quantity = item.get('quantity', 0)
            calories_per_unit = item.get('calories_per_unit', 0)
            total_calories += quantity * calories_per_unit

        return jsonify({'total_calories': total_calories}), 200
    
    except KeyError as e:
        return jsonify({'error': f'Missing key {str(e)} in input data'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/calorie_2', methods=['POST'])
def calculate_calories_2():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        items = data['items']
        total_calories = 0

        # Loop through each item to calculate total calories
        for item in items:
            name = item.get('name', 'Unknown')
            quantity = item.get('quantity', 0)
            calories_per_unit = item.get('calories_per_unit', 0)
            total_calories += quantity * calories_per_unit

        return jsonify({'total_calories': total_calories}), 200

    except KeyError as e:
        return jsonify({'error': f'Missing key {str(e)} in input data'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
