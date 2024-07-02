from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
import cv2
import base64
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    image = db.Column(db.String(100), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        
        if user:
            return redirect(url_for('stored'))
        
        image_data = request.form['image']
        image_parts = image_data.split(',');
        if len(image_parts) == 2:
                image_bytes = base64.b64decode(image_parts[1])
        else:
                flash('Invalid image data.', 'danger')
                return redirect(url_for('register'))
        image_filename = f'{email}.jpg'
        image_path = os.path.join('static', 'images', image_filename)
        with open(image_path, 'wb') as f:
            f.write(image_bytes)

        if image_path:
            new_user = User(email=email, image=image_path)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Please upload an image.', 'warning')
            return redirect(url_for('register'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        image_data = request.form['image']
        image_parts = image_data.split(',');
        if len(image_parts) == 2:
                image_bytes = base64.b64decode(image_parts[1])
        else:
                flash('Invalid image data.', 'danger')
                return redirect(url_for('error'))

        
        temp_image_path = os.path.join('static', 'temp', f'{email}_temp.jpg')
        with open(temp_image_path, 'wb') as f:
            f.write(image_bytes)

        if image_data:
            # Load stored image and uploaded image using OpenCV
            user = User.query.filter_by(email=email).first()
            if user:
                stored_image_path = user.image
                stored_image = cv2.imread(stored_image_path, cv2.IMREAD_GRAYSCALE)
                uploaded_image = cv2.imread(temp_image_path, cv2.IMREAD_GRAYSCALE)

                # Compare the images using OpenCV's compareHist function (histogram comparison)
                similarity = cv2.compareHist(cv2.calcHist([stored_image], [0], None, [256], [0, 256]),
                                             cv2.calcHist([uploaded_image], [0], None, [256], [0, 256]),
                                             cv2.HISTCMP_CORREL)

                # Define a threshold for similarity (adjust as needed)
                similarity_threshold = 0.8

                if similarity > similarity_threshold:
                    flash('Authentication successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Authentication failed. Please try again.', 'danger')
                    return redirect(url_for('error'))

            else:
                flash('User not found. Please register.', 'warning')
                return redirect(url_for('error'))
        else:
            flash('Please upload an image.', 'warning')
            return redirect(url_for('img_corr'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Check if user is authenticated and display dashboard
    return render_template('dashboard.html')
@app.route('/img_corr')
def img_corr():
    # Check if user is authenticated and display dashboard
    return render_template('img_corr.html')

@app.route('/error')
def error():
    # Check if user is authenticated and display error
    return render_template('error.html')

@app.route('/stored')
def stored():
    # Check if user is authenticated and display info
    return render_template('stored.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)
