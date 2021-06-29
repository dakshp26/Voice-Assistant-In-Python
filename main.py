from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import os
import time
import speech_recognition as sr
import pyttsx3
import pytz

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
DAY_EXTENSIONS = ["rd", "th", "st", "nd"]
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said=""
        try:
            said = r.recognize_google(audio)
            print("Me:" + said)
        except Exception as e:
            print("Exception: "+str(e))
    return said.lower()

def authenticate_google():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service

def get_events(day, service):
    # Call the Calendar API
    date = datetime.datetime.combine(day, datetime.datetime.min.time())   #minimum time on the day
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time()) #maximum time on the particular day

    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)
    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(),timeMax=end_date.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
        print("No upcoming events found")
    else:
        if len(events)==1:
            print(f"You have {len(events)} event on this day")
            speak(f"You have {len(events)} event on this day")
        else:
            print(f"You have {len(events)} events on this day")
            speak(f"You have {len(events)} events on this day")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("+")[0])
            if int(start_time.split(":")[0]) < 12:
                start_time = start_time + "am"
            else:
                start_time = str(int(start_time.split(":")[0])-12) + ":" + start_time.split(":")[1]
                start_time = start_time + "pm"
            print(event["summary"]+ " at " + start_time)
            speak(event["summary"]+ " at " + start_time)

def get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today
    if text.count("tomorrow") > 0:
        return datetime.date.today() + datetime.timedelta(days=1)

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1  #converts the month in no. like september = 9 as our list is in order
        elif word in DAYS:
            day_of_week = DAYS.index(word)   #converts day into number ofr datetime module
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENSIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    #condition to check if we are asking for a day within the month of next year
    if month < today.month and month != -1 :
        year = year + 1

    #condition to check if we are talking the present month's date or next month's date, so if that date has passed it would choose date from next month
    if day < today.day and month == -1 and day != -1:
        month = month + 1

    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()  #0-6
        dif = day_of_week - current_day_of_week



        if dif < 0:
            dif += 7
            if text.count("next") > 0:
                dif += 7

        return today + datetime.timedelta(dif)
    # if month == -1 or day == -1:
    #     return None
    # return datetime.date(month=month, day=day, year=year)
    if day != -1:
        return datetime.date(month=month, day=day, year=year)

def take_note(text):
    date = datetime.datetime.now()
    file_name = str(date).replace(":", "-") + "-note.txt"

    directory = "notes"
    parent_dir = os.getcwd()
    path = os.path.join(parent_dir, directory)
    if not os.path.isdir("notes"):
        try:
            os.makedirs(path, exist_ok=True)

        except OSError as error:
            print("could not note")
    else:
        pass

    with open("notes/"+file_name,"w") as f:
        f.write(text)
    location = "notes\\"+file_name
    os.startfile(location)


#WAKE is the keyword which will awaken our assistant 
WAKE = "hello"
SERVICE = authenticate_google()
while True:
    print("Listening")
    text = get_audio()
    if text.count(WAKE) > 0:
        speak("Yes sir. How can I help you?")
        text = get_audio()
        CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy"]

        for phrase in CALENDAR_STRS:
            if phrase in text:
                date = get_date(text)
                if date:
                   get_events(get_date(text), SERVICE)
                else:
                    speak("I dont understand")

        NOTE_STRS = ["make a note", "write this down", "remember this"]

        for phrase in NOTE_STRS:
            if phrase in text:
                speak("What would you like me to write down?")
                note_text = get_audio()
                take_note(note_text)
                speak("I have made a note of that.")

