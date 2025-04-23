from datetime import datetime
from time import localtime, strftime
import os
import time
import requests
import json
import webbrowser

version = "1"

def calcTimeSignIn():
    rawtime = localtime()
    timeasdt = datetime.now()
    if int(rawtime.tm_hour) > 12:
        hour = int(rawtime.tm_hour) - 12
    else:
        hour = int(rawtime.tm_hour)

    timestring = (str(rawtime.tm_mon) + "/" + str(rawtime.tm_mday) + "/" + str(rawtime.tm_year) + ", " + str(hour) + ":" + timeasdt.strftime("%M") + ":00 " + timeasdt.strftime("%p"))
    return timestring
    
def calcTimeRoster():
    rawtime = localtime()
    timeasdt = datetime.now()
    if int(rawtime.tm_hour) > 12:
        hour = int(rawtime.tm_hour) - 12
    else:
        hour = int(rawtime.tm_hour)

    timestring = (str(rawtime.tm_mon) + "/" + str(rawtime.tm_mday) + "/" + str(rawtime.tm_year) + ", " + str(hour) + ":" + timeasdt.strftime("%M") + ":" + timeasdt.strftime("%S") + " " + timeasdt.strftime("%p"))
    return timestring
    
def dumpInfo():
    s = requests.Session()
    try:
        l = s.post('https://' + os.environ['subdomain'] + '.demschooltools.com/login', data={'noredirect': '', 'email': str(os.environ['checkinemail']), 'password': str(os.environ['checkinpass'])})
    except:
        print("Could not connect to server! Please try again!")
        time.sleep(5)
        exit(100)
    calcTimeRoster()

    r = s.get('https://' + os.environ['subdomain'] + '.demschooltools.com/attendance/checkin/data', params={'time': calcTimeRoster()})
    j = r.json()["people"]
    for i in range(len(j)):
        if j[i]["name"] == "Admin":
            j.pop(i)
            break
    file = open("response.json", "w")
    json.dump(j, file, indent = 4)
    file.close
    print("Dumped response data to response.json")

def prompt():
    os.system("cls")
    print(
'''
 .d8888b.  888                        888            d8b                .d8888b.  888      8888888 
d88P  Y88b 888                        888            Y8P               d88P  Y88b 888        888   
888    888 888                        888                              888    888 888        888   
888        88888b.   .d88b.   .d8888b 888  888       888 88888b.       888        888        888   
888        888 "88b d8P  Y8b d88P"    888 .88P       888 888 "88b      888        888        888   
888    888 888  888 88888888 888      888888K 888888 888 888  888      888    888 888        888   
Y88b  d88P 888  888 Y8b.     Y88b.    888 "88b       888 888  888      Y88b  d88P 888        888   
 "Y8888P"  888  888  "Y8888   "Y8888P 888  888       888 888  888       "Y8888P"  88888888 8888888

By Logan - Version ''' + version + ''' - Type "help" to view the documentation.
This version does not automatically check for updates.
'''
    )
    global personid
    global name
    personid = input('Enter PersonID, Name, PIN, or Command: ')
    if personid == "debug":
        try:
            import debug
        except FileNotFoundError:
            print("Debug module not found!")
            time.sleep(5)
        exit(100)
    elif personid == "docs" or personid == "help":
        webbrowser.open_new_tab("https://miamisudbury.github.io/checkin/docs/v" + version)
        print("Opened version " + version + " documentation in your browser!")
        time.sleep(5)
        prompt()
    else:
        try:
            file = open("response.json", "r")
        except FileNotFoundError:
            print("Could not find response file! Attempting to generate response file...")
            dumpInfo()
            file = open("response.json", "r")
        people = json.load(file)
        searchfor = personid
        found = False
        for i in people:
            if (i["name"]) == searchfor or (i["pin"]) == searchfor or (str(i["personId"])) == searchfor:
                if (i["name"]) == "Admin":
                    print("You cannot sign in as this user!")
                    time.sleep(5)
                    exit(100)
                personid = int(i["personId"])
                name = i["name"]
                found = True
        if found != True:
            print("The specified person could not be found. Did you type the info correctly? (See documentation: Troubleshooting for more info.)")
            time.sleep(5)
            exit(100)
    return personid

# CODE STARTS EXECUTING HERE

try:
    os.environ['subdomain']
    os.environ['checkinemail']
    os.environ['checkinpass']
except: # if this fails, we don't have the environment variables we need!
    print("WARNING: One or more required environment variables are not present! Read documentation for more info!")
    print("Please set the variables and run the script again.")
    time.sleep(10)
    exit(2)

prompt()

arriving = input("Are you signing in or out? ")

if arriving == "in":
    isArriving = "true"
elif arriving == "out":
    isArriving = "false"
else:
    print("Answer must be in/out")
    time.sleep(3)
    exit(2)
# Asks if the user is arriving or leaving, and sets the appropriate request parameters. If an invalid answer is given, exit.
# Case sensitive!

s = requests.Session()
# Create a session to store the login cookie.

try:
    l = s.post('https://' + os.environ['subdomain'] + '.demschooltools.com/login', data={'noredirect': '', 'email': str(os.environ['checkinemail']), 'password': str(os.environ['checkinpass'])})
except:
    print("Could not connect to server! Please try again!")
    time.sleep(3)
    exit(2)
payload = {'time_string': calcTimeSignIn(), 'personId': personid, 'is_arriving': isArriving}
r = s.post('https://' + os.environ['subdomain'] + '.demschooltools.com/attendance/checkin/message', params=payload)

if r.status_code == 200:
    print("Successfully signed " + name + " " + arriving + "!")
else:
    print("Failed to sign " + arriving + " with status code " + str(r.status_code))
time.sleep(2)
