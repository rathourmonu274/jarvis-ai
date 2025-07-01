import pyttsx3
import speech_recognition as sr
import eel
import time


def speak(text):
    # text = str(text)
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.setProperty("rate", 170)
    engine.setProperty('volume', 1.0)
    eel.DisplayMessage(text)
    engine.say(text)
    engine.runAndWait()

# it is the speaker of the program.


@eel.expose
def takecommand():

    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('say something....')
        eel.DisplayMessage('say something....')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, 3, 2)
    try:
        print('recognizing')
        eel.DisplayMessage('recognizing....')
        query = r.recognize_google(audio, language="en-in")
        print("user said: " + query)
        eel.DisplayMessage(query)
        time.sleep(2)
    except Exception as e:
        print("please try again.....")

    return query.lower()
    # except Exception as e:
    #     time.sleep(2)


@eel.expose
def allCommands():

    query = takecommand()
    print = (query)

    if "open" in query:
        from engine.feature import openCommand
        openCommand(query)
    else:
        print("not run")

    eel.ShowHood()