from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import json
import urllib.request 
from CountryNames import get_countryName

load_dotenv('.env')
api = os.getenv('API_KEY')

app = Flask(__name__) 

@app.route('/', methods =['POST', 'GET']) 
def weather(): 
	if request.method == 'POST': 
		city = request.form['city'] 

		city = city.strip().title()
	else: 
		# default city name 
		city = 'Pune'
  
	try:
		# Fetch data from OpenWeather API
		source = urllib.request.urlopen(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api}&units=metric').read() 
						
		# converting JSON data to a dictionary 
		list_of_data = json.loads(source)

  		# Extract country code from API response
		country_code = list_of_data['sys']['country']
		
  		# Use get_countryName from CountryNames.py to get the country name
		country_name = get_countryName(country_code)
  
		# Data for variable list_of_data 
		data = { 
			"city_name" : city,
			"country_name": country_name, 
			"temp": str(list_of_data['main']['temp']) + " °C", 
			"humidity": str(list_of_data['main']['humidity']) + " %", 
			"clouds" : str(list_of_data['clouds']['all']) + "%",
			"wind" : str(round(list_of_data['wind']['speed'] * 3.6, 2)) + " kph",
			"visibility" : str(list_of_data['visibility'] / 1000) + " km",
			"icon": f"http://openweathermap.org/img/wn/{list_of_data['weather'][0]['icon']}@2x.png",
			"description": list_of_data['weather'][0]['description'].capitalize()
		} 
  
	except Exception as e:
        # If an error occurs, return an error message
		data = {
      			"error" : "Enter valid city name!"
        }

	return render_template('index.html', data=data) 

@app.route('/aboutus')
def aboutus():
    return render_template('about.html')


if __name__ == '__main__': 
	app.run(debug = True) 
