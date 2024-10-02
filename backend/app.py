from flask import Flask, request, jsonify, abort
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from flask_cors import CORS
from pydantic import BaseModel
from calorie_estimate import (
    CalorieEstimate,
    encode_image,
    get_calorie_estimate_text,
    get_calorie_estimate_image
)


app = Flask(__name__)
CORS(app)  # Add this line after creating the Flask app
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'fallback-secret-key' # Change this to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['UPLOAD_FOLDER'] = 'uploads'


# Ensure the upload folder exists
upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)

app.config['UPLOAD_FOLDER'] = upload_folder


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
    food_name = db.Column(db.String(255), nullable=False)
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

@app.route('/api/user', methods=['GET'])
@login_required
def get_user():
    user = User.query.get(current_user.id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user_data = {
        'id': user.id,
        'username': user.username,
        'weight': user.weight,
        'desired_weight': user.desired_weight
    }
    
    return jsonify(user_data), 200



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


@app.route('/api/goal_weight', methods=['POST'])
@login_required
def goal_weight():
    data = request.get_json()
    new_weight = data.get('goal_weight')
    
    if new_weight is None:
        return jsonify({'error': 'Weight not provided'}), 400
    
    current_user.desired_weight = new_weight
    db.session.commit()
    
    return jsonify({'message': 'Weight updated successfully'}), 200



@app.route('/api/add_calorie_entry', methods=['POST'])
@login_required
def add_calorie_entry():
    data = request.get_json()
    calories = data.get('calories')
    food_name = data.get('food_name')
    
    if not calories or not food_name:
        return jsonify({'error': 'Calories and food name not provided'}), 400
    
    entry = CalorieEntry(user_id=current_user.id, calories=float(calories), food_name=food_name)
    db.session.add(entry)
    db.session.commit()
    
    return jsonify({'message': 'Calorie entry added successfully'}), 201

@app.route('/api/calorie_history', methods=['GET'])
@login_required
def get_calorie_history():
    entries = CalorieEntry.query.filter_by(user_id=current_user.id).order_by(CalorieEntry.date.desc()).all()
    history = [{
        'id': entry.id,
        'food_name': entry.food_name,
        'calories': entry.calories,
        'date': entry.date.isoformat()
    } for entry in entries]
    return jsonify(history), 200

@app.route('/api/estimate_calories_from_image', methods=['POST'])
def estimate_calories_from_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No selected image file'}), 400

    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
         
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)

        try:
            base64_image = encode_image(image_path)
            calorie_estimate = get_calorie_estimate_image(base64_image)

            return jsonify({
                'food_name': calorie_estimate.food_name,
                'calories': calorie_estimate.calories,
                'protein': calorie_estimate.protein,
                'carbs': calorie_estimate.carbs,
                'fat': calorie_estimate.fat,
                'serving_size': calorie_estimate.serving_size,
                'confidence': calorie_estimate.confidence,
                'additional_info': calorie_estimate.additional_info
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


@app.route('/api/estimate_calories_from_text', methods=['POST'])
def estimate_calories_from_text():
    data = request.get_json()

    if not data or 'food_description' not in data:
        return jsonify({'error': 'No food description provided'}), 400

    food_description = data['food_description']

    try:
        calorie_estimate = get_calorie_estimate_text(food_description)

        return jsonify({
            'food_name': calorie_estimate.food_name,
            'calories': calorie_estimate.calories,
            'protein': calorie_estimate.protein,
            'carbs': calorie_estimate.carbs,
            'fat': calorie_estimate.fat,
            'serving_size': calorie_estimate.serving_size,
            'confidence': calorie_estimate.confidence,
            'additional_info': calorie_estimate.additional_info
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
