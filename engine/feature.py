import json
import re
import os
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from shlex import quote
import sqlite3
import struct
import subprocess
import time
import eel
import webbrowser
import hugchat
import pvporcupine
import pyaudio
import pyautogui
import pywhatkit as kit
from sqlite3 import Cursor
from playsound import playsound
from engine.command import speak
from engine.config import ASSISTANT_NAME
from engine.helper import extract_yt_term, remove_words
from hugchat import hugchat

conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()


@eel.expose
def playassitantsound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)


def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()

    app_name = query.strip()

    if app_name != "":

        try:
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0:
                cursor.execute(
                    'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()

                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")


def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)


# FAV_SONG = "pal pal dil ke pass"
# def PlayFavSongSpotify():
#     speak("Playing your favourite song on Spotify")
#     spotify_url = f"https://open.spotify.com/search/{FAV_SONG.replace(' ', '%20')}"
#     webbrowser.open(spotify_url)


# def PlaySpotify(query):
#     search_term = query.replace(ASSISTANT_NAME, "").replace(
#         "play", "").replace("on spotify", "").strip()
#     speak("Playing " + search_term + " on Spotify")
#     spotify_url = f"https://open.spotify.com/search/{search_term.replace(' ', '%20')}"
#     webbrowser.open(spotify_url)

# 1) Put your credentials here
CLIENT_ID = "8d047983d0f345e3a0473bbf738823d8"
CLIENT_SECRET = "25a94c4c05404af890d074996b1c29d7"
REDIRECT_URI = "http://localhost:8888/callback"
SCOPE = "user-read-playback-state,user-modify-playback-state"

# 2) Global client (token cache ho jayega .spotipy_cache me)
_sp = None


def sp_client():
    global _sp
    if _sp is None:
        _sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
            open_browser=True,          # first time auth ke liye browser khulega
            cache_path=".spotipy_cache"  # token cache
        ))
    return _sp

# 3) Ensure active device (desktop/mobile app) to play on


def ensure_active_device(sp):
    devices = sp.devices().get("devices", [])
    if devices:
        # prefer active device
        for d in devices:
            if d.get("is_active"):
                return d["id"]
        # else pick first + transfer playback
        target_id = devices[0]["id"]
        sp.transfer_playback(device_id=target_id, force_play=False)
        return target_id

    # try to launch Spotify app (Windows)
    try:
        os.system("start spotify")
    except:
        pass

    time.sleep(2)
    devices = sp.devices().get("devices", [])
    if devices:
        target_id = devices[0]["id"]
        sp.transfer_playback(device_id=target_id, force_play=False)
        return target_id

    return None

# 4) Main autoplay function (exact song play)


def PlaySpotifyAutoplay(song_name: str):
    sp = sp_client()
    try:
        device_id = ensure_active_device(sp)
        if not device_id:
            speak("Open Spotify app once, then try again.")
            return

        res = sp.search(q=song_name, type="track", limit=1)
        items = res.get("tracks", {}).get("items", [])
        if not items:
            speak("Sorry, I couldn't find that song on Spotify.")
            return

        track = items[0]
        track_uri = track["uri"]
        track_url = track["external_urls"]["spotify"]

        sp.start_playback(device_id=device_id, uris=[track_uri])
        speak(f"Playing {track['name']} on Spotify")
    except spotipy.SpotifyException as e:
        # 403 usually = not premium
        try:
            status = e.http_status
        except:
            status = None
        if status == 403:
            speak(
                "Spotify Premium is required for autoplay via API. Opening in browser instead.")
            webbrowser.open(track_url)
        else:
            speak("Something went wrong with Spotify.")
            print("SpotifyException:", e)


# Optional: fav song helper
FAV_SONG = "pal pal dil ke paas"


def PlayFavSongSpotifyAutoplay():
    PlaySpotifyAutoplay(FAV_SONG)

# (Old fallback) Only open search page—no autoplay


def PlaySpotify(query):
    search_term = (query.replace(ASSISTANT_NAME, "")
                        .replace("play", "")
                        .replace("on spotify", "")
                        .strip())
    speak("Opening Spotify search for " + search_term)
    webbrowser.open(
        f"https://open.spotify.com/search/{search_term.replace(' ', '%20')}")
# ---------- End Spotify block ----------


def hotword():
    porcupine = None
    paud = None
    audio_stream = None
    try:

        # pre trained keywords
        porcupine = pvporcupine.create(keywords=["jarvis", "alexa"])
        paud = pyaudio.PyAudio()
        audio_stream = paud.open(rate=porcupine.sample_rate, channels=1,
                                 format=pyaudio.paInt16, input=True, frames_per_buffer=porcupine.frame_length)

        # loop for streaming
        while True:
            keyword = audio_stream.read(porcupine.frame_length)
            keyword = struct.unpack_from("h"*porcupine.frame_length, keyword)

            # processing keyword comes from mic
            keyword_index = porcupine.process(keyword)

            # checking first keyword detetcted for not
            if keyword_index >= 0:
                print("hotword detected")

                # pressing shorcut key win+j
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")

    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()


# find contacts
def findContact(query):

    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'tu',
                       'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?",
                       ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0


def whatsApp(mobile_no, message, flag, name):

    if flag == 'message':
        target_tab = 21
        jarvis_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 13
        message = ''
        jarvis_message = "calling to "+name

    else:
        target_tab = 12
        message = ''
        jarvis_message = "staring video call with "+name

    # Encode the message for URL
    encoded_message = quote(message)
    print(encoded_message)
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)

    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)

# chat bot


def chatBot(query):
    user_input = query.lower()
    chatbot = hugchat.ChatBot(cookie_path="engine/cookies.json")
    id = chatbot.new_conversation()
    chatbot.change_conversation(id)
    response = chatbot.chat(user_input)
    print(response)
    speak(response)
    return response

# android automation


def makeCall(name, mobileNo):
    mobileNo = mobileNo.replace(" ", "")
    speak("Calling "+name)
    command = 'adb shell am start -a android.intent.action.CALL -d tel:'+mobileNo
    os.system(command)


# to send message
# def sendMessage(message, mobileNo, name):
#     from engine.helper import replace_spaces_with_percent_s, goback, keyEvent, tapEvents, adbInput
#     message = replace_spaces_with_percent_s(message)
#     mobileNo = replace_spaces_with_percent_s(mobileNo)
#     speak("sending message")
#     goback(4)
#     time.sleep(1)
#     keyEvent(3)
#     # open sms app
#     tapEvents(136, 2220)
#     # start chat
#     tapEvents(819, 2192)
#     # search mobile no
#     adbInput(mobileNo)
#     # tap on name
#     tapEvents(601, 574)
#     # tap on input
#     tapEvents(390, 2270)
#     # message
#     adbInput(message)
#     # send
#     tapEvents(957, 1397)
#     speak("message send successfully to "+name)

# import google.generativeai as genai
# def geminai(query):
#     try:
#         query = query.replace(ASSISTANT_NAME, "")
#         query = query.replace("search", "")
#         # Set your API key
#         genai.configure(api_key=LLM_KEY)

#         # Select a model
#         model = genai.GenerativeModel("gemini-2.0-flash")

#         # Generate a response
#         response = model.generate_content(query)
#         filter_text = markdown_to_text(response.text)
#         speak(filter_text)
#     except Exception as e:
#         print("Error:", e)


# Settings Modal


# Assistant name
@eel.expose
def assistantName():
    name = ASSISTANT_NAME
    return name


@eel.expose
def personalInfo():
    try:
        cursor.execute("SELECT * FROM info")
        results = cursor.fetchall()
        jsonArr = json.dumps(results[0])
        eel.getData(jsonArr)
        return 1
    except:
        print("no data")


@eel.expose
def updatePersonalInfo(name, designation, mobileno, email, city):
    cursor.execute("SELECT COUNT(*) FROM info")
    count = cursor.fetchone()[0]

    if count > 0:
        # Update existing record
        cursor.execute(
            '''UPDATE info 
               SET name=?, designation=?, mobileno=?, email=?, city=?''',
            (name, designation, mobileno, email, city)
        )
    else:
        # Insert new record if no data exists
        cursor.execute(
            '''INSERT INTO info (name, designation, mobileno, email, city) 
               VALUES (?, ?, ?, ?, ?)''',
            (name, designation, mobileno, email, city)
        )

    conn.commit()
    personalInfo()
    return 1


@eel.expose
def displaySysCommand():
    cursor.execute("SELECT * FROM sys_command")
    results = cursor.fetchall()
    jsonArr = json.dumps(results)
    eel.displaySysCommand(jsonArr)
    return 1


@eel.expose
def deleteSysCommand(id):
    cursor.execute("DELETE FROM sys_command WHERE id = ?", (id,))
    conn.commit()


@eel.expose
def addSysCommand(key, value):
    cursor.execute(
        '''INSERT INTO sys_command VALUES (?, ?, ?)''', (None, key, value))
    conn.commit()


@eel.expose
def displayWebCommand():
    cursor.execute("SELECT * FROM web_command")
    results = cursor.fetchall()
    jsonArr = json.dumps(results)
    eel.displayWebCommand(jsonArr)
    return 1


@eel.expose
def addWebCommand(key, value):
    cursor.execute(
        '''INSERT INTO web_command VALUES (?, ?, ?)''', (None, key, value))
    conn.commit()


@eel.expose
def deleteWebCommand(id):
    cursor.execute("DELETE FROM web_command WHERE Id = ?", (id,))
    conn.commit()


@eel.expose
def displayPhoneBookCommand():
    cursor.execute("SELECT * FROM contacts")
    results = cursor.fetchall()
    jsonArr = json.dumps(results)
    eel.displayPhoneBookCommand(jsonArr)
    return 1


@eel.expose
def deletePhoneBookCommand(id):
    cursor.execute("DELETE FROM contacts WHERE Id = ?", (id,))
    conn.commit()


@eel.expose
def InsertContacts(Name, MobileNo, Email, City):
    cursor.execute(
        '''INSERT INTO contacts VALUES (?, ?, ?, ?, ?)''', (None, Name, MobileNo, Email, City))
    conn.commit()
