import os
import eel
from engine.feature import *
from engine.command import *
from engine.auth import recoganize


def start():
    eel.init("www")

    playassitantsound()

    flag = recoganize.AuthenticateFace()

    os.system('start msedge.exe --app="http://localhost:8000/index.html"')
    eel.start('index.html', mode=None, host='localhost', block=True)
