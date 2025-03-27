from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from tinydb import TinyDB, Query
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "skrivni_kljuc_123"  # V produkciji uporabi pravi skrivni ključ!

db = TinyDB('CustomCloset.json')
users = db.table('users')
User = Query()

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

if __name__ == "__main__":
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(debug=True)