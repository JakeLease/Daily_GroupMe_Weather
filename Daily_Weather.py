import Weather_Fuctions as WF
import Test_File as test
import time
import threading

def main():
	# getting info from user
	print("Please Enter the follow parameters:")
	gmAPIKep = input(
		"Please enter the GroupMe API token key (you can get it by signing in at https://dev.groupme.com/) : ")
	print(f"Go to https://api.groupme.com/v3/groups?token={gmAPIKep} to get the group name you wish to use. ")
	gmGroupName = input("Please enter the Group name you wish to post to: ")
	GroupMe = WF.GroupMe_Request(gmAPIKep, gmGroupName)
	# checks if API key was correct
	while 0 == GroupMe.make_request(""):
		print("That API Key did not work please try a new one")
		gmAPIKep = input(
			"Please enter the GroupMe API token key (you can get it by signing in at https://dev.groupme.com/) : ")
		GroupMe = WF.GroupMe_Request(gmAPIKep, gmGroupName)
	# check if group name was correct and found
	while 0 == GroupMe.get_group_id():
		print("That was not found.")
		gmGroupName = input("Please enter the Group name you wish to post to: ")
		GroupMe = WF.GroupMe_Request(gmAPIKep, gmGroupName)

	print(
		"Now Enter the parameters for Open Weather\nIf you do not have an API Key visit https://openweathermap.org/ and sign up")
	weatherAPIKey = input("Please Enter your Open Weather API Key: ")
	cityName = input("Enter the city you would like to monitor: ")
	cityName = cityName.title()
	Weather = WF.Weather_Request(weatherAPIKey, cityName)
	# Checking if the city asked for is in json file
	while 0 == Weather.get_city_id(cityName):
		cityName = input("That city was not found\nPlease Enter the city you would like to monitor: ")
		cityName = cityName.title()
		Weather = WF.Weather_Request(weatherAPIKey, cityName)
		while 0 == Weather.make_request(""):
			weatherAPIKey = input("API did not Work please try again\nEnter your Open Weather API Key: ")
			Weather = WF.Weather_Request(weatherAPIKey, cityName)

	x = False
	while not x:
		GroupMe.check_messages(Weather)


if __name__ == "__main__":
	timeLimit = input("Enter how long should this program run ( in HHMMSS format ): ")
	hourTime = int(timeLimit[0:2]) * 60 * 60
	minuteTime = int(timeLimit[2:4]) * 60
	secondTIme = int(timeLimit[4:6])
	timeLimit = hourTime + hourTime + secondTIme
	mainThreading = threading.Thread(target=main)
	mainThreading.daemon = True
	mainThreading.start()
	time.sleep(timeLimit)
	print("Time limit reached. Ending Program")
# ToDO: add GUI, clean code, add time limit set by user

