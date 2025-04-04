from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from tinydb import TinyDB, Query
import os

app = Flask(__name__)
app.secret_key = "skrivni_kljuc_123"

db = TinyDB('CustomCloset.json')
users = db.table('users')
images_db = db.table('images')
User = Query()

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/home")
def home():
    slika = "https://www.opremisidom.com/wp-content/uploads/2023/03/20.84.1002.00_1800x1800.webp"
    return render_template("home.html", slika = slika)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(User.username == username)
        
        if user:
            if user['password'] == password:
                session['username'] = username
                return jsonify({'success': True})
            return jsonify({'success': False, 'error': 'Wrong password'})
        
        users.insert({'username': username, 'password': password})
        session['username'] = username
        return jsonify({'success': True})
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/closet')
def closet():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("closet.html")

@app.route('/closet/<category>')
def closet_category(category):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username, category)
    
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    images = images_db.search((User.username == username) & (User.category == category))
    
    # Popravi poti, da so relativne do `static/uploads/`
    image_urls = [img['file_path'].replace("\\", "/") for img in images]

    return render_template(f"{category}.html", category=category, images=image_urls)

@app.route('/upload/<category>', methods=['POST'])
def upload_image(category):
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})

    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username, category)

    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})

    filename = secure_filename(file.filename)
    file_path = os.path.join(user_folder, filename)
    file.save(file_path)

    # Popravi pot, da je pravilna za HTML
    relative_path = file_path.replace("\\", "/")

    images_db.insert({'username': username, 'category': category, 'file_path': relative_path})

    return jsonify({'success': True, 'file_path': f"/{relative_path}"})

@app.route('/uploads/<username>/<category>/<filename>')
def uploaded_file(username, category, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], username, category), filename)

@app.route("/outfitcreation")
def outfitcreation():
    return render_template("outfitCreation.html")

@app.route('/get_images/<category>')
def get_images(category):
    if 'username' not in session:
        return jsonify({'images': []})

    username = session['username']
    images = images_db.search((User.username == username) & (User.category == category))
    image_urls = [url_for('uploaded_file', username=username, category=category, filename=img['file_path'].split('/')[-1]) for img in images]

    return jsonify({'images': image_urls})

if __name__ == "__main__":
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True)