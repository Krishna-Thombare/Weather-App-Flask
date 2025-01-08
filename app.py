from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from config import Config
import os
import json
import urllib.request
from CountryNames import get_countryName
from models import db, User, SavedCity

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)  # Load configuration from Config class

# Initialize extensions
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['POST', 'GET'])
def weather():
    api_key = os.getenv('API_KEY')
    saved_cities = []
    
    if current_user.is_authenticated:
        saved_cities = SavedCity.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST':
        city = request.form['city']
        city = city.strip().title()
    else:
        city = 'Pune'

    try:
        # Fetch data from OpenWeather API
        source = urllib.request.urlopen(
            f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric').read()

        # converting JSON data to a dictionary
        list_of_data = json.loads(source)

        # Extract country code from API response
        country_code = list_of_data['sys']['country']

        # Use get_countryName from CountryNames.py to get the country name
        country_name = get_countryName(country_code)

        # Data for variable list_of_data
        data = {
            "city_name": city,
            "country_name": get_countryName(list_of_data['sys']['country']),
            "temp": str(list_of_data['main']['temp']) + " °C",
            "humidity": str(list_of_data['main']['humidity']) + " %",
            "clouds": str(list_of_data['clouds']['all']) + "%",
            "wind": str(round(list_of_data['wind']['speed'] * 3.6, 2)) + " km/h",
            "visibility": str(list_of_data['visibility'] / 1000) + " km",
            "icon": f"http://openweathermap.org/img/wn/{list_of_data['weather'][0]['icon']}@2x.png",
            "description": list_of_data['weather'][0]['description'].capitalize(),
        }

    except Exception as e:
        data = {"error": "Enter valid city name!"}

    return render_template('index.html', data=data, api_key=api_key, saved_cities=saved_cities)

@app.route('/aboutus')
def aboutus():
    return render_template('about.html')

@app.route('/save_city/<city_name>')
@login_required
def save_city(city_name):
    if SavedCity.query.filter_by(user_id=current_user.id).count() >= 3:
        flash('You can only save up to 3 cities.')
        return redirect(url_for('weather'))
    
    # Check for duplicates
    if not SavedCity.query.filter_by(user_id=current_user.id, city_name=city_name).first():
        city = SavedCity(city_name=city_name, user_id=current_user.id)
        db.session.add(city)
        db.session.commit()
        flash(f'{city_name} has been added to your saved cities.')
    else:
        flash(f'{city_name} is already in your saved cities.')
    
    return redirect(url_for('weather'))

@app.route('/remove_city/<city_name>')
@login_required
def remove_city(city_name):
    city = SavedCity.query.filter_by(user_id=current_user.id, city_name=city_name).first()
    if city:
        db.session.delete(city)
        db.session.commit()
        flash(f'{city_name} has been removed from your saved cities.')
    return redirect(url_for('weather'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
            
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful!')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('weather'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('weather'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)