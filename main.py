#git config --global user.name jakisa0
#git config --global user.name jakakosir5@gmail.com
#pip install tinydb flask

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




#------------------------------------------trade------------------------------------------
from werkzeug.datastructures import FileStorage
from tinydb.operations import set
import uuid

# Nova tabela za oglase
ads_db = db.table('ads')

@app.route('/oglas', methods=['GET', 'POST'])
def oglas():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        image = request.files.get('image')
        size = request.form.get('size')
        contact = request.form.get('contact')
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        username = session['username']

        if not image or not size or not contact:
            return jsonify({'success': False, 'error': 'Missing fields'})

        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'ads')
        os.makedirs(image_path, exist_ok=True)
        full_path = os.path.join(image_path, filename)
        image.save(full_path)

        image_url = f"/uploads/ads/{filename}"

        ad_id = str(uuid.uuid4())
        ads_db.insert({
            'id': ad_id,
            'username': username,
            'image': image_url,
            'size': size,
            'contact': contact,
            'lat': float(lat),
            'lon': float(lon)
        })

        return redirect(url_for('trade'))

    return render_template('oglas.html')

@app.route('/trade')
def trade():
    if 'username' not in session:
        return redirect(url_for('login'))

    ads = ads_db.all()
    return render_template('trade.html', ads=ads)

@app.route('/uploads/ads/<filename>')
def uploaded_ad_image(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'ads'), filename)

if __name__ == "__main__":
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True)