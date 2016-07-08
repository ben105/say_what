# Say What?
This script listens to meetings I'm supposed to be paying attention to and pings me on hipchat when my name is mentioned.

It sends me a transcript of what was said in the minute before my name was mentioned and some time after. 

It also plays an audio file out loud 15 seconds after my name was mentioned which is a recording of me saying, "Sorry, I didn't realize my mic was on mute there."

Uses IBM's Speech to Text Watson API for the audio-to-text. 

This script will utilize Sqlite3 to store the minutes locally, in the SQL database. Future enhancement will include deleting aged data, to prevent scaling issues and wasted disk space.

Relies on Uberi's SpeechRecognition PyAudio and API wrapper: https://github.com/Uberi/speech_recognition

##Installation (OS X)

1. [Get a hipchat API token](https://[your company].hipchat.com/account/api) and update the hipchat fields in say\_my\_name.py
	* Your hipchat user id is the second number in your hipchat jabber info
2. Update ```name``` in say\_my\_name.py unless your name is Ben
3. [Create an IBM Bluemix account](https://console.ng.bluemix.net/registration/)
4. [Add a speech-to-text plan](https://new-console.ng.bluemix.net/catalog/services/speech-to-text/)
5. Add your credentials to say\_what.py for ```IBM_USERNAME``` and ```IBM_PASSWORD```
6. [Install Homebrew](http://brew.sh/)
7. ```brew install python```
8. ```brew install portaudio```
9. ```pip install pyaudio```
10. ```pip install SpeechRecognition```
11. ```pip install requests```

##Usage

Run the following in the terminal:
```python say_what.py```

### TODO: Improve usage
