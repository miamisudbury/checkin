import os
import time
from time import localtime, strftime
import requests
from datetime import datetime
import json

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
        exit(10)
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

def evalUser():
    global personid
    global name
    global people
    global searchfor # are these last 4 necessary? probably not
    global found
    global file
    global out
    personid = input('Enter PersonID, Name, or PIN of user to check: ')
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
            if (i["name"]) == "Admin": # no clue if this check is even necessary
                print("You cannot view the data of this user!")
                time.sleep(5)
                exit(100)
            personid = int(i["personId"])
            name = i["name"]
            found = True
            out = json.dumps(i, indent=2)
    if found != True:
        print("The specified person could not be found. Did you type the info correctly? (See documentation: Troubleshooting for more info.)")
        time.sleep(5)
        exit(100)
    return personid

os.system('cls')
print('''

8888888b.  8888888888 888888b.   888     888  .d8888b.  
888  "Y88b 888        888  "88b  888     888 d88P  Y88b 
888    888 888        888  .88P  888     888 888    888 
888    888 8888888    8888888K.  888     888 888        
888    888 888        888  "Y88b 888     888 888  88888 
888    888 888        888    888 888     888 888    888 
888  .d88P 888        888   d88P Y88b. .d88P Y88b  d88P 
8888888P"  8888888888 8888888P"   "Y88888P"   "Y8888P88 

Remember to use debug utilities responsibly! :)
''')
print('''
[1] Dump Roster Info
[2] Get Person Info [+ Dump Roster Info]
[3] List Users Not Signed In [+ Dump Roster Info]
[4] List Users Not Signed Out [+ Dump Roster Info]
[X] Exit Debug & Check-in Program
''')
selectedOption = input('Choose Debug Option: ')

if selectedOption == "X" or selectedOption == "x":
    exit(2)

elif selectedOption == '1':
    dumpInfo()
    time.sleep(3)

elif selectedOption == '2':
    dumpInfo()
    evalUser()
    try:
        print(out)
    except:
        print("The user you are trying to look for could not be found. Did you type their ID correctly?")

    time.sleep(10)
    # Returns raw (formatted) JSON. 

elif selectedOption == '3':
    dumpInfo()
    file = open("response.json", "r")
    people = json.load(file)
    personIndex = -1
    personList = []
    peopleNotSignedInCount = 0
    for i in people:
        personIndex += 1
        personList.append(personIndex)
        if (i["name"]) == "Admin": # redundant check?
            continue
        if (i["current_day_start_time"]) == None:
            print(str(personIndex) + " - " + i["name"] + " - " + str(i["personId"]))
            peopleNotSignedInCount += 1
    if peopleNotSignedInCount == 0:
        print("Hooray! Everyone is signed in!")
        time.sleep(5)
        exit(3)
    btoggle = True
    while btoggle == True:
        print("Enter Index ID to sign in. 'X' to cancel.")
        tosign = int(input("ID: "))
        if tosign == "X" or tosign == "x":
            btoggle = False
        ind = -1
        for i in people:
            ind += 1
            if ind == tosign:
                pid = i["personId"]
                payload = {'time_string': calcTimeSignIn(), 'personId': pid, 'is_arriving': "true"}
                try:
                    s = requests.Session()
                    l = s.post('https://' + os.environ['subdomain'] + '.demschooltools.com/login', data={'noredirect': '', 'email': str(os.environ['checkinemail']), 'password': str(os.environ['checkinpass'])})
                    r = s.post('https://' + os.environ['subdomain'] + '.demschooltools.com/attendance/checkin/message', params=payload)
                except:
                    print("Unable to connect to the server! Please try again when you have a stable connection")
                    time.sleep(5)
                    exit(6)
                if r.status_code == 200:
                    print("Successfully signed " + i["name"] + " in!")
                else:
                    print("Failed to sign in " + i["name"] + " with status code " + r.status_code + "!")
                
    time.sleep(10)
elif selectedOption == '4':
    dumpInfo()
    file = open("response.json", "r")
    people = json.load(file)
    personIndex = -1
    personList = []
    peopleNotSignedOutCount = 0
    for i in people:
        personIndex += 1
        personList.append(personIndex)
        if (i["name"]) == "Admin": # redundant check?
            continue
        if (i["current_day_end_time"]) == None:
            print(str(personIndex) + " - " + i["name"] + " - " + str(i["personId"]))
            peopleNotSignedOutCount += 1
    if peopleNotSignedOutCount == 0:
        print("Hooray! Everyone is signed out!")
        time.sleep(5)
        exit(3)
    btoggle = True
    while btoggle == True:
        print("Enter Index ID to sign out. 'X' to cancel.")
        tosign = int(input("ID: "))
        if tosign == "X" or tosign == "x":
            btoggle = False
        ind = -1
        for i in people:
            ind += 1
            if ind == tosign:
                pid = i["personId"]
                payload = {'time_string': calcTimeSignIn(), 'personId': pid, 'is_arriving': "false"}
                try:
                    s = requests.Session()
                    l = s.post('https://' + os.environ['subdomain'] + '.demschooltools.com/login', data={'noredirect': '', 'email': str(os.environ['checkinemail']), 'password': str(os.environ['checkinpass'])})
                    r = s.post('https://' + os.environ['subdomain'] + '.demschooltools.com/attendance/checkin/message', params=payload)
                except:
                    print("Unable to connect to the server! Please try again when you have a stable connection")
                    time.sleep(5)
                    exit(6)
                if r.status_code == 200:
                    print("Successfully signed " + i["name"] + " out!")
                else:
                    print("Failed to sign out " + i["name"] + " with status code " + r.status_code + "!")
                
                
    time.sleep(10)

else:
    print("Invalid Option. Exiting...")
    time.sleep(1.5)
