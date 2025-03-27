#pip install tinydb flask

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from tinydb import TinyDB, Query
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "skrivni_kljuc_123"  # V produkciji uporabi pravi skrivni ključ!

db = TinyDB('CustomCloset.json')
users = db.table('users')
images_db = db.table('images')
User = Query()


#mapa za shranjevanje slik oblek
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
        try:
            username = request.form['username']
            password = request.form['password']
            
            user = users.get(User.username == username)
            
            if user:
                if user['password'] == password:
                    session['username'] = username

                    return jsonify({'success': True})
                    
                else:
                    return jsonify({'success': False, 'error': 'Wrong password'})
            else:
                users.insert({'username': username, 'password': password})

                session['username'] = username
                return jsonify({'success': True})
                
        except Exception as e:
            print(f"Napaka pri prijavi: {str(e)}")
            return jsonify({'success': False, 'error': 'Prišlo je do napake'})
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/closet')
def closet():
    if 'username' not in session:   #brez pijave ne moraš dostopati do /closet
        return redirect(url_for('login'))
    return render_template("closet.html")

@app.route('/closet/<category>', methods=['GET', 'POST'])  # povezava na različne albume
def closet_category(category):
    if 'username' not in session:
        return redirect(url_for('login')) 
    
    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username, category)
    
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    images = images_db.search((User.username == username) & (User.category == category))
    print("Images in database:", images)  # Dodaj ta print, da preveriš vsebino seznama slik

    image_urls = [url_for('uploaded_file', username=username, category=category, filename=img['file_path'].split('/')[-1]) for img in images]
    print("Image URLs:", image_urls)  # Dodaj ta print, da preveriš ustvarjene URL-je za slike

    return render_template(f"{category}.html", category=category, images=image_urls)


@app.route('/upload/<category>', methods=['POST'])
def upload_image(category):
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})

    username = session['username']
    # Pot za shranjevanje slike, vključno z uporabniškim imenom in kategorijo
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username, category)

    # Preveri, ali mapa obstaja, če ne, jo ustvari
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    # Preveri, ali je bila datoteka poslana
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})

    file = request.files['file']

    # Preveri, ali je ime datoteke prazno
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})

    # Preveri ime datoteke (uporabi varno ime za datoteko)
    filename = secure_filename(file.filename)
    file_path = os.path.join(user_folder, filename)  # Pot do datoteke v ustrezni mapi
    file.save(file_path)  # Shrani datoteko

    # Shrani podatke o sliki v bazo z relativno potjo, ki vključuje 'static/'
    image_url = os.path.join('static', username, category, filename)  # Relativna pot do slike
    images_db.insert({'username': username, 'category': category, 'file_path': image_url})

    # Pošlji pot do slike v odgovoru
    return jsonify({'success': True, 'file_path': f"/uploads/{username}/{category}/{filename}"})

@app.route('/uploads/<username>/<category>/<filename>')
def uploaded_file(username, category, filename):
    # Preberi sliko iz ustrezne mape in jo pošlji uporabniku
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], username, category), filename)

if __name__ == "__main__":
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True)