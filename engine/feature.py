from playsound import playsound
import eel
from engine.command import speak
from engine.config import ASSISTANT_NAME
import os


@eel.expose
def playassitantsound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)


def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()


    if query!= "":
      speak("opening"+query)
      os.system('start'+query)
    else:
      speak("not found")
