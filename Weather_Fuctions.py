import requests
from requests.exceptions import HTTPError
import json
import uuid
import logging
import time

logger = logging.getLogger(__name__)

# request class for groupme calls
class GroupMe_Request:
	def __init__(self, API_key, group_name):
		self.base_URL = 'https://api.groupme.com/v3/groups?token='
		self.API_key = API_key
		self.group_name = group_name

	# get group ID by finding group name user entered
	def get_group_id(self):
		api_request = self.make_request("")
		api_json = api_request.json() # TODO: make it so when make_request doesnt cause it to crash when it fails and returns a 0
		group_name = ''
		i = 0
		while self.group_name != group_name:
			group_name = api_json['response'][i]['name']
			if self.group_name == group_name:
				group_id = api_json['response'][i]['id']
				return group_id
			i += 1
			if i == 10:
				return 0

	def make_request(self, url):
		# if "" is passed then we use default value
		if "" == url:
			base_url = self.base_URL
			api_key = self.API_key
			url = base_url + api_key

		try:
			api_request = requests.get(url)
			if 400 <= int(api_request.status_code):
				return 0
		except HTTPError as err:
			logger.error(err, extra={url})
			return 0
		else:
			return api_request

	def get_group_url(self):
		group_id = self.get_group_id()
		return self.base_URL[:-7] + "/" + group_id + "/messages?token=" + self.API_key

	def make_post(self, text):
		url = self.get_group_url()
		GUID = str(uuid.uuid4())
		data = {
			"message": {
				"source_guid": GUID,
				"text": text,

			}
		}
		postWeather = requests.post(url=url, json=data)

		# checks groups messages
	def check_messages(self, weatherClass):
		api_request = self.make_request(self.get_group_url())
		api_request = api_request.json()
		textContents = api_request['response']['messages'][0]['text']
		if textContents == '!weather':
			text = createText(weatherClass, "")
			self.make_post(text)
			time.sleep(9)
		elif textContents[0] == "!":
			textContents = textContents[1:]
			# if user enters a city then it will post for that city, if not then post main city
			if 0 != weatherClass.get_city_id(textContents):
				text = createText(weatherClass, textContents)
				self.make_post(text)
				time.sleep(9)
			else:
				self.make_post("City not found try again in 1 minute")
				time.sleep(30)

		time.sleep(1.2)

# class for requesting weather
class Weather_Request:
	def __init__(self,  API_key, city_name, timeout=10):
		self.base_URL = 'https://api.openweathermap.org/data/2.5/forecast?id='
		self.API_key = API_key
		self.city_name = city_name
		self.timeout = timeout

	def get_city_id(self, city_name):
		# if "" is passed then we use default value
		if "" == city_name:
			city_name = self.city_name
		json_file = "city_list.json"
		with open(json_file, encoding="utf8") as file:
			data = json.load(file)
			for name in data:
				if name['name'] == city_name:
					file.close()
					return str(name['id'])
			file.close()
			return 0

	def make_request(self, city_name):
		if "" == city_name:
			city_name = self.city_name
		if 0 == self.get_city_id(city_name):
			return 0
		url = self.base_URL + self.get_city_id(city_name) + "&appid=" + self.API_key
		try:
			api_request = requests.get(url)
			if 400 <= int(api_request.status_code):
				return 0
		except HTTPError as err:
			logger.error(err, extra={url})
			return 0
		else:
			return api_request

# a function for deciding most frequent
def most_frequent(L):
	counter = 0
	num = L[0]

	for i in L:
		curr_frequency = L.count(i)
		if curr_frequency > counter:
			counter = curr_frequency
			num = i

	return num

# function for deciding weather data
def getInfoFromWeatherAPI(weatherClass, stringText):
	weatherJson = weatherClass.json()

	if stringText == 'temp_min':
		i = 0
		tempsMin = [0 for x in range(8)]
		# access API and gets temps for day and stores it
		while i != 8:
			tempsMin[i] = ((float(weatherJson['list'][i]['main']['temp_min']) - 273.15) * (9 / 5) + 32)
			i += 1

		i = 0
		lowestTemp = 300
		for x in tempsMin:
			# sets lowest temp
			if lowestTemp >= x:
				lowestTemp = x

		lowestTemp = round(lowestTemp, 2)
		return lowestTemp
	# for max temp
	if stringText == 'temp_max':
		tempMax = [0 for x in range(8)]
		i = 0
		# access API and gets temps for day and stores it
		while i != 8:
			tempMax[i] = ((float(weatherJson['list'][i]['main']['temp_max']) - 273.15) * (9 / 5) + 32)
			i += 1

		highestTemp = 0
		for x in tempMax:
			# sets highest temp
			if highestTemp <= x:
				highestTemp = x

		highestTemp = round(highestTemp, 2)
		return highestTemp
	# for humidity
	if stringText == 'humidity':
		humidityList = [0 for x in range(8)]
		i = 0
		# access API and gets humidity for day and stores it
		while i != 8:
			humidityList[i] = (float(weatherJson['list'][i]['main']['humidity']))
			i += 1
		# get average humidity
		avgHumidity = 0
		for x in humidityList:
			avgHumidity += x

		avgHumidity /= 8

		avgHumidity = round(avgHumidity, 2)
		return avgHumidity

	# for wind speed
	if stringText == 'wind':
		windList = [0 for x in range(8)]
		i = 0
		# access API and gets wind speed for day and stores it
		while i != 8:
			windList[i] = (float(weatherJson['list'][i]['wind']['speed']) * 2.23694)
			i += 1

			# get average humidity
		avgWind = 0
		for x in windList:
			avgWind += x

		avgWind /= 8

		avgWind = round(avgWind, 2)
		return avgWind

	# cardinal direction wind is blowing
	if stringText == 'wind direction':
		windList = [0 for x in range(8)]
		i = 0
		# access API and gets wind speed for day and stores it
		while i != 8:
			windList[i] = (float(weatherJson['list'][i]['wind']['deg']) )
			i += 1

			# get average humidity
		avgWind = 0
		for x in windList:
			avgWind += x

		avgWind /= 8
		if 361<= avgWind:
			return "no where"
		avgWind = round(avgWind, 2)
		if 337.5 < avgWind <=360 or 0 <= avgWind <= 22.5:
			return "North"
		elif 22.5 < avgWind <= 67.5:
			return "Northeast"
		elif 67.5 < avgWind <= 112.5:
			return "East"
		elif 112.5 < avgWind <= 157.5:
			return "Southeast"
		elif 2157.5 < avgWind <= 202.5:
			return "South"
		elif 202.5 < avgWind <= 247.5:
			return "Southwest"
		elif 247.5 < avgWind <= 292.5:
			return "West"
		elif 292.5 < avgWind <= 337.5:
			return "Northwest"

	if stringText == 'weather':
		weatherListID = []
		i = 0
		# access API and gets weather ID for day and stores it
		while i != 8:
			weatherListID.append(weatherJson['list'][i]['weather'][0]['id'])
			i += 1

		# dictionary's for all weather ID codes and Descriptions
		weatherDictMain = {
			'200': 'Thunderstorms', '201': 'Thunderstorms', '202': 'Thunderstorms', '210': 'Thunderstorms',
			'211': 'Thunderstorms',
			'212': 'Thunderstorms', '221': 'Thunderstorms', '230': 'Thunderstorms', '231': 'Thunderstorms',
			'232': 'Thunderstorms',
			'300': 'Drizzle', '301': 'Drizzle', '302': 'Drizzle', '310': 'Drizzle', '311': 'Drizzle', '312': 'Drizzle',
			'313': 'Drizzle',
			'314': 'Drizzle', '321': 'Drizzle', '500': 'Rain', '501': 'Rain', '502': 'Rain', '503': 'Rain',
			'504': 'Rain',
			'511': 'Rain', '520': 'Rain', '521': 'Rain', '522': 'Rain', '531': 'Rain', '600': 'Snow', '601': 'Snow',
			'602': 'Snow',
			'611': 'Snow', '612': 'Snow', '613': 'Snow', '615': 'Snow', '616': 'Snow', '620': 'Snow', '621': 'Snow',
			'622': 'Snow', '701': 'Mist', '711': 'Smoke', '721': 'Haze', '731': 'Dust', '741': 'Fog', '751': 'Sand',
			'761': 'Dust', '762': 'ASh', '771': 'Squall',
			'781': 'Tornado', '800': 'Clear', '801': 'Clouds', '802': 'Clouds', '803': 'Clouds', '804': 'Clouds'
		}
		weatherDictDescription = {
			'200': 'thunderstorm with light rain', '201': 'thunderstorm with rain',
			'202': 'thunderstorm with heavy rain', '210': 'light thunderstorm',
			'211': 'thunderstorm', '212': 'heavy thunderstorm', '221': 'ragged thunderstorm',
			'230': 'thunderstorm with light drizzle',
			'231': 'thunderstorm with drizzle', '232': 'thunderstorm with heavy drizzle',
			'300': 'light intensity drizzle', '301': 'drizzle', '302': 'heavy intensity drizzle',
			'310': 'light intensity drizzle rain', '311': 'drizzle rain', '312': 'heavy intensity drizzle rain',
			'313': 'shower rain and drizzle', '314': 'heavy shower rain and drizzle', '321': 'shower drizzle',
			'500': 'light rain', '501': 'moderate rain', '502': 'heavy intensity rain', '503': 'very heavy rain',
			'504': 'extreme rain',
			'511': 'freezing rain', '520': 'light intensity shower rain', '521': 'shower rain',
			'522': 'heavy intensity shower rain', '531': 'ragged shower rain', '600': 'light snow', '601': 'snow',
			'602': 'heavy snow', '611': 'sleet', '612': 'light shower sleet', '613': 'shower sleet',
			'615': 'light rain and snow', '616': 'rain and snow', '620': 'light shower snow', '621': 'shower snow',
			'622': 'heavy shower snow', '701': 'mist', '711': 'smoke', '721': 'haze', '731': 'dust', '741': 'fog',
			'751': 'sand',
			'761': 'dust', '762': 'ash', '771': 'squall',
			'781': 'tornado', '800': 'clear sky', '801': 'few clouds', '802': 'scattered clouds',
			'803': 'broken clouds', '804': 'overcast clouds'
		}
		# for keeping track how many different codes in one day to narrow down weather
		twoHun = 0
		threeHun = 0
		fiveHun = 0
		sixHun = 0
		sevenHun = 0
		eightHun = 0

		for x in weatherListID:
			intID = int(x)
			if 200 <= x <= 299:
				twoHun += 1
			elif 300 <= x <= 399:
				threeHun += 1
			elif 500 <= x <= 599:
				fiveHun += 1
			elif 600 <= x <= 699:
				sixHun += 1
			elif 700 <= x <= 799:
				sevenHun += 1
			elif 800 <= x <= 899:
				eightHun += 1
			else:
				return 'No weather today'

		# two most frequent weather that day
		codeList = {'200': twoHun, '300': threeHun, '500': fiveHun, '600': sixHun, '700': sevenHun, '800': eightHun}
		firstFrequent = max(codeList.values())
		firstFrequent = [x for x, y in codeList.items() if y == firstFrequent]
		mostFreq = firstFrequent[0]
		del codeList[firstFrequent[0]]

		secFreq = 0
		secondFrequent = max(codeList.values())
		if secondFrequent != 0:
			secondFrequent = [x for x, y in codeList.items() if y == secondFrequent]
			secFreq = secondFrequent[0]
			del codeList[secondFrequent[0]]

		# finds which weather ID is most common and uses that
		mostFreqDescription = most_frequent(weatherListID)
		mostFreqDescription = str(mostFreqDescription)
		# short cut to say if most frequent description does not match the most frequent main ID
		if mostFreqDescription[0] != mostFreq[0]:
			return f" Weather today will consist of {weatherDictMain[mostFreq]} as well as some {weatherDictDescription[mostFreqDescription]}. "

		# returns the string we will have sent out
		main_string = ''
		if secFreq != 0:
			if mostFreq == '200':
				main_string = f"Today it looks like it is going to {weatherDictDescription[mostFreqDescription]} so you better bring a rain jacket! "
				if secFreq == '600':
					main_string += "It also looks like we are going to have some snow today as well. "
				elif secFreq == '300':
					main_string += "It also looks like the rain is going to slow down to a drizzle for some time today. "
				elif secFreq == '700':
					sevenID = ''
					for x in weatherListID:
						if x[0] == '7':
							main_string += f"It also looks like we are going to have some weird weather in the form of {weatherDictDescription[x]}. WOW that's some weird weather!!! "
							break
				elif secFreq == '800':
					for x in weatherListID:
						if x == '800':
							main_string += "Don't worry though, the weather will clear up and we will have some clear sky's. "
							break
						elif x[0] == '8':
							main_string += f"The rain will stop and we will have {weatherDictDescription[x]} for some time today. "
							break
				return main_string
			elif mostFreq == '300':
				main_string = f"Today it looks like it is going to {weatherDictDescription[mostFreqDescription]} so you better bring a rain jacket! "
				if secFreq == '600':
					main_string += "It also looks like we are going to have some snow today as well. "
				elif secFreq == '200':
					main_string += "It also looks like the rain is going to pick up to a thunderstorm at some point today. "
				elif secFreq == '700':
					sevenID = ''
					for x in weatherListID:
						if x[0] == '7':
							main_string += f"It also looks like we are going to have some weird weather in the form of {weatherDictDescription[x]}. WOW that's some weird weather!!! "
							break
				elif secFreq == '800':
					for x in weatherListID:
						if x == '800':
							main_string += "Don't worry though, the weather will clear up and we will have some clear sky's. "
							break
						elif x[0] == '8':
							main_string += f"The rain will stop and we will have {weatherDictDescription[x]} for some time today. "
							break
				return main_string
			elif mostFreq == '500':
				main_string = f"Today it looks like it is going to {weatherDictDescription[mostFreqDescription]} so you better bring a rain jacket! "
				if secFreq == '600':
					main_string += "It also looks like we are going to have some snow today as well. "
				elif secFreq == '300':
					main_string += "It also looks like the rain is going to slow down to a drizzle for some time today. "
				elif secFreq == '200':
					main_string += "It also looks like the rain is going to pick up to a thunderstorm at some point today. "
				elif secFreq == '700':
					sevenID = ''
					for x in weatherListID:
						if x[0] == '7':
							main_string += f"It also looks like we are going to have some weird weather in the form of {weatherDictDescription[x]}. WOW that's some weird weather!!! "
							break
				elif secFreq == '800':
					for x in weatherListID:
						if x == '800':
							main_string += "Don't worry though, the weather will clear up and we will have some clear sky's. "
							break
						elif x[0] == '8':
							main_string += f"The rain will stop and we will have {weatherDictDescription[x]} for some time today. "
							break
				return main_string
			elif mostFreq == '600':
				main_string = f"Today it looks like it is going to {weatherDictDescription[mostFreqDescription]} so you better dress warm and wear some snow boots. "
				main_string += "Don't slip and fall!!! "
				if secFreq == '200':
					main_string += "It also looks like the snow will stop and we will get a thunderstorm which could melt the snow. "
				elif secFreq == '300':
					main_string += "It also looks like the snow is going to slow down to a drizzle for some time today. "
				elif secFreq == '500':
					main_string += "It also looks like the snow is going to turn into rain, so be careful of the slush when driving. "
				elif secFreq == '700':
					sevenID = ''
					for x in weatherListID:
						if x[0] == '7':
							main_string += f"It also looks like we are going to have some weird weather in the form of {weatherDictDescription[x]}. WOW that's some weird weather!!! "
							break
				elif secFreq == '800':
					for x in weatherListID:
						if x == '800':
							main_string += "Don't worry though, the weather will clear up and we will have some clear sky's. "
							break
						elif x[0] == '8':
							main_string += f"The rain will stop and we will have {weatherDictDescription[x]} for some time today. "
							break
				return main_string
			elif mostFreq == '700':
				main_string = f"Today it looks we are going to have {weatherDictDescription[mostFreqDescription]} so dress appropriate. "
				if secFreq == '200':
					main_string += "It looks like we could get a thunderstorm at some point today. "
				elif secFreq == '600':
					main_string += "It also looks like we are going to have some snow today as well. "
				elif secFreq == '300':
					main_string += "It looks like we could get some drizzle at some point today. "
				elif secFreq == '500':
					main_string += "It looks like we could get some rain at some point today. "
				elif secFreq == '800':
					for x in weatherListID:
						if x == '800':
							main_string += "Don't worry though, the weather will clear up and we will have some clear sky's. "
							break
						elif x[0] == '8':
							main_string += f"Looks like we will have {weatherDictDescription[x]} for some time today. "
							break
				return main_string
			elif mostFreq == '800':
				if mostFreqDescription == '800':
					main_string = "Looks like we are going to have a beautiful day with some clear sky's. enjoy the weather today. "
				else:
					main_string = f"Today it looks like there are going to be some {weatherDictDescription[mostFreqDescription]} so don't be sad maybe tomorrow it will be sunny!  "
				if secFreq == '600':
					main_string += "It also looks like we are going to have some snow today as well. "
				elif secFreq == '200':
					main_string += "It does look like a chance of thunderstorms today. "
				elif secFreq == '300':
					main_string += "It does look like it might drizzle a little bit today. "
				elif secFreq == '500':
					main_string += "It there might be a chance of some rain. "
				elif secFreq == '700':
					sevenID = ''
					for x in weatherListID:
						if x[0] == '7':
							main_string += f"It also looks like we are going to have some weird weather in the form of {weatherDictDescription[x]}. WOW that's some weird weather!!! "
							break
				return main_string
		else:
			if mostFreq == '200':
				main_string = f"Today it looks like it is going to {weatherDictDescription[mostFreqDescription]} so you better bring a rain jacket! "
				return main_string
			elif mostFreq == '300':
				main_string = f"Today it looks like it is going to {weatherDictDescription[mostFreqDescription]} so you better bring a rain jacket! "
				return main_string
			elif mostFreq == '500':
				main_string = f"Today it looks like it is going to {weatherDictDescription[mostFreqDescription]} so you better bring a rain jacket! "
				return main_string
			elif mostFreq == '600':
				main_string = f"Today it looks like it is going to {weatherDictDescription[mostFreqDescription]} so you better dress warm and wear some snow boots. "
				main_string += "Don't slip and fall!!! "
				return main_string
			elif mostFreq == '700':
				main_string = f"Today it looks we are going to have {weatherDictDescription[mostFreqDescription]} so dress appropriate. "
				return main_string
			elif mostFreq == '800':
				if mostFreqDescription == '800':
					main_string = "Looks like we are going to have a beautiful day with some clear sky's. enjoy the weather today. "
				else:
					main_string = f"Today it looks like there are going to be some {weatherDictDescription[mostFreqDescription]} so don't be sad maybe tomorrow it will be sunny!  "
				return main_string

# creates text to be posted
def createText(weatherClass, city_Name):
	intro = ''
	if "" != city_Name:
		intro = f"The Weather in today in {city_Name} is: "
	else:
		intro = f"The Weather in today in {weatherClass.city_name} is: "

	tempString = f"Today there will be a high of {getInfoFromWeatherAPI(weatherClass.make_request(city_Name), 'temp_max')} degrees and a low of {getInfoFromWeatherAPI(weatherClass.make_request(city_Name), 'temp_min')} degrees. "
	wind = getInfoFromWeatherAPI(weatherClass.make_request(city_Name), 'wind')
	windString = ''
	if wind > 5:
		windString = f"There will be strong gusts of winds coming from the {getInfoFromWeatherAPI(weatherClass.make_request(city_Name), 'wind direction')}, blowing at {wind} MPH. "
	humidityString = f"There will be a humidity of {getInfoFromWeatherAPI(weatherClass.make_request(city_Name), 'humidity')}. "
	weatherString = getInfoFromWeatherAPI(weatherClass.make_request(city_Name), 'weather')
	finalPrintString = "Hello there people of this group, " + intro
	finalPrintString += tempString + windString + humidityString + weatherString + "Have a good day and use this information to plan accordingly "
	return finalPrintString
