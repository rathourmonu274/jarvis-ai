import pyttsx3
import speech_recognition as sr
import eel
import time
import os


def speak(text):
    # text = str(text)
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.setProperty("rate", 170)
    engine.setProperty('volume', 1.0)
    eel.DisplayMessage(text)
    engine.say(text)
    eel.receiverText(text)
    engine.runAndWait()

# it is the speaker of the program.


# @eel.expose
def takecommand():

    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('say something....')
        eel.DisplayMessage('say something....')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, 6, 5)
    try:
        print('recognizing')
        eel.DisplayMessage('recognizing....')
        query = r.recognize_google(audio, language="en-in")
        print("user said: " + query)
        eel.DisplayMessage(query)
        time.sleep(2)
    except Exception as e:
        return ""
    return query.lower()
    # except Exception as e:
    #     time.sleep(2)


@eel.expose
def allCommands(message=1):

    if message == 1:
        query = takecommand()
        print(query)
        eel.senderText(query)
    else:
        query = message
        eel.senderText(query)

    try:
        if "open" in query:
            from engine.feature import openCommand
            openCommand(query)
        elif "on youtube" in query:
            from engine.feature import PlayYoutube
            PlayYoutube(query)

        elif "send message" in query or "phone call" in query or "video call" in query:
            from engine.feature import findContact, whatsApp, makeCall  # sendMessage
            flag = ""
            contact_no, name = findContact(query)
            if (contact_no != 0):
                speak("Which mode you want to use whatsapp or mobile")
                preferance = takecommand()
                print(preferance)

                if "mobile" in preferance:
                    if "send message" in query or "send sms" in query:
                        speak("what message to send boss")
                        message = takecommand()
                        # sendMessage(message, contact_no, name)
                    elif "phone call" in query:
                        makeCall(name, contact_no)
                    else:
                        speak("please try again")
                elif "whatsapp" in preferance:
                    message = ""
                    if "send message" in query:
                        flag = 'message'
                        speak("what message to send")
                        query = takecommand()

                    elif "phone call" in query:
                        flag = 'call'
                    else:
                        flag = 'video call'

                    whatsApp(contact_no, query, flag, name)
            else:
                  from engine.feature import chatBot
        chatBot(query)
    except:
        print("error")

    eel.ShowHood()
