# Voice Assistant In Python

The voice assistant has a wake keyword to which it responds when person around the mic says it.

It provides the following functionality:
- Tells us about the day's events using Google Calendar API and automatically identifies the day we are talking about 
(Eg: "what do i have on monday?" will return a list of events for the upcoming monday so the user doesnt have to provide date and be very specific)
- Wite a note for us
(Eg: "make a note" will trigger the assistant to make a note of anything we say after it says "What would you like me to write down?")

Have used the following libraries for this project:
1. pyttsx3
2. pickle
3. datetime
4. pytz
5. speech_recognition
6. time
7. os
8. google libraries for calendar api

Note: I have not included the credentials.json and token.pickle files so you would have to create them on your own by signing up for google calendar's account and obtaining your own credentials.json and token.pickle file.
