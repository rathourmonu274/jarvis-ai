import os
import eel
from engine.feature import *
from engine.command import *


def start():
    eel.init("www")

    playassitantsound()

    os.system('start msedge.exe --app="http://localhost:8000/index.html"')
    eel.start('index.html', mode=None, host='localhost', block=True)
