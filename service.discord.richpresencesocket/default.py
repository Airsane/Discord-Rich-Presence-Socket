import xbmc, xbmcaddon
import json
import time
import re
import requests


#SERVER CUSTOM SCRIPT

import socket 
import threading

HEADER = 64
PORT = 5050
SERVER = "" #Host IP example 192.168.0.22
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
running = False



def log(msg):
    xbmc.log("[Discord RP] " + msg)

DISCORD_CLIENT_ID = '0'
CLIENT_ID = ['544620244014989312',
             '570950300446359552']


def getShowImage(showTitle):
    if showTitle in AVAIABLE_IMAGES:
        return AVAIABLE_IMAGES[showTitle]
    return "default"


def removeKodiTags(text):
    log("Removing tags for: " + text)

    validTags = ["I", "B", "LIGHT", "UPPERCASE", "LOWERCASE", "CAPITALIZE", "COLOR"]
    
    for tag in validTags:
        r = re.compile("\[\s*/?\s*"+tag+"\s*?\]")
        text = r.sub("", text)

    r = re.compile("\[\s*/?\s*CR\s*?\]")
    text = r.sub(" ", text)

    r = re.compile("\[\s*/?\s*COLOR\s*?.*?\]")
    text = r.sub("", text)

    log("Removed tags. Result: " + text)

    return text


class ServiceRichPresence:
    def __init__(self):
        self.presence = None
        self.settings = {}
        self.paused = True
        self.connected = False

        self.updateSettings()
        self.clientId = self.settings['client_id']

    def setPauseState(self, state):
        self.paused = state

    def updateSettings(self):
        self.settings = {}
        self.settings['large_text'] = "Kodi"

        addon = xbmcaddon.Addon()
        
        self.settings['episode_state'] = addon.getSettingInt('episode_state')
        self.settings['episode_details'] = addon.getSettingInt('episode_details')
        self.settings['movie_state'] = addon.getSettingInt('movie_state')
        self.settings['movie_details'] = addon.getSettingInt('movie_details')

        self.settings['inmenu'] = addon.getSettingBool('inmenu')
        self.settings['client_id'] = addon.getSettingInt('client_id')

        # get setting
        log(str(self.settings))

    def gatherData(self):
        player = xbmc.Player()
        if player.isPlayingVideo():
            return player.getVideoInfoTag()
            
        return None

    def craftNoVideoState(self, data):
        if self.settings['inmenu']:
            activity = {'assets' : {'large_image' : 'default',
                                  'large_text' : self.settings['large_text']},
                        'state' : (self.settings['inmenu'] and 'In menu' or '')
                        }
            return activity
        else:
            return None

    def getEpisodeState(self, data):
        if self.settings['episode_state'] == 0:
            return '{}x{:02} {}'.format(data.getSeason(),data.getEpisode(),removeKodiTags(data.getTitle()))
        if self.settings['episode_state'] == 1:
            return data.getTVShowTitle()
        if self.settings['episode_state'] == 2:
            return data.getGenre()
        return None

    def getEpisodeDetails(self, data):
        if self.settings['episode_details'] == 0:
            return data.getTVShowTitle()
        if self.settings['episode_details'] == 1:
            return '{}x{:02} {}'.format(data.getSeason(),data.getEpisode(),removeKodiTags(data.getTitle()))
        if self.settings['episode_details'] == 2:
            return data.getGenre()
        return None

    def craftEpisodeState(self, data):
        activity = {}
        activity['assets'] = {'large_image' : getShowImage(data.getTVShowTitle()),
                              'large_text' : data.getTVShowTitle()}

        state = self.getEpisodeState(data)
        if state:
            activity['state'] = state

        details = self.getEpisodeDetails(data)
        if details:
            activity['details'] = details
        return activity

    def getMovieState(self, data):
        if self.settings['movie_state'] == 0:
            return data.getGenre()
        if self.settings['movie_state'] == 1:
            return removeKodiTags(data.getTitle())
        return None

    def getMovieDetails(self, data):
        if self.settings['movie_details'] == 0:
            return removeKodiTags(data.getTitle())
        if self.settings['movie_details'] == 1:
            return data.getGenre()
        return None

    def craftMovieState(self, data):
        activity = {}
        activity['assets'] = {'large_image' : 'default',
                              'large_text' : removeKodiTags(data.getTitle())}

        state = self.getMovieState(data)
        if state:
            activity['state'] = state

        details = self.getMovieDetails(data)
        if details:
            activity['details'] = details 
        return activity

    def craftVideoState(self, data):
        activity = {}

        title = data.getTitle() or data.getTagLine() or data.getFile()
        title = removeKodiTags(title)

        activity['assets'] = {'large_image' : 'default',
                              'large_text' : title }

        activity['details'] = title

        return activity

    def mainLoop(self):
        while True:
            monitor.waitForAbort(5)
            if monitor.abortRequested():
                break
            self.updatePresence()
        log("Abort called. Exiting...")
        if self.connected:
            try:
                global running,client
                running = False
                if client:
                    client.close()
                server.close()
            except IOError as e:
                self.connected = False
                log("Error closing connection: " + str(e))

    def updatePresence(self):
        self.connected = True
        if self.connected:
            data = self.gatherData()

            activity = None
            #activity['assets'] = {'large_image' : 'default',
            #                        'large_text' : self.settings['large_text']}

            if not data:
                # no video playing
                log("Setting default")
                if self.settings['inmenu']:
                    activity = self.craftNoVideoState(data)
            else:
                if data.getMediaType() == 'episode':
                    activity = self.craftEpisodeState(data)
                elif data.getMediaType() == 'movie':
                    activity = self.craftMovieState(data)
                elif data.getMediaType() == 'video':
                    activity = self.craftVideoState(data)
                else:
                    activity = self.craftVideoState(data)
                    log("Unsupported media type: "+str(data.getMediaType()))
                    log("Using workaround")

                if self.paused:
                    activity['assets']['small_image'] = 'paused'
                    # Works for
                    #   xx:xx/xx:xx
                    #   xx:xx/xx:xx:xx
                    #   xx:xx:xx/xx:xx:xx
                    currentTime = player.getTime()
                    hours = int(currentTime/3600)
                    minutes = int(currentTime/60) - hours*60
                    seconds = int(currentTime) - minutes*60 - hours*3600

                    fullTime = player.getTotalTime()
                    fhours = int(fullTime/3600)
                    fminutes = int(fullTime/60) - fhours*60
                    fseconds = int(fullTime) - fminutes*60 - fhours*3600
                    activity['assets']['small_text'] = "{}{:02}:{:02}/{}{:02}:{:02}".format('{}:'.format(hours) if hours>0 else '',
                                                               minutes,
                                                               seconds,
                                                               '{}:'.format(fhours) if fhours>0 else '',
                                                               fminutes,
                                                               fseconds
                                )

                else:
                    currentTime = player.getTime()
                    fullTime = player.getTotalTime()
                    remainingTime = fullTime - currentTime
                    activity['timestamps'] = {'end' : int(time.time()+remainingTime)}
            
            if activity == None:
                try:
                    self.presence.clear_activity()
                except Exception as e:
                    log("Error while clearing: " + str(e))
            else:
                if self.settings['client_id'] != self.clientId:
                    pass
                else:
                    log("Activity set: " + str(activity))
                    global client
                    try:         
                        if client:
                            client.sendall(bytes(str(activity),'utf-8'))
                    except:
                        client = None




class MyPlayer(xbmc.Player):
    def __init__(self):
        xbmc.Player.__init__(self)

    def onPlayBackPaused(self):
        drp.setPauseState(True)
        drp.updatePresence()

    def onAVChange(self):
        drp.updatePresence()

    def onAVStarted(self):
        drp.setPauseState(False)
        drp.updatePresence()

    def onPlayBackEnded(self):
        drp.setPauseState(True)
        drp.updatePresence()

    def onPlayBackResumed(self):
        drp.setPauseState(False)
        drp.updatePresence()

    def onPlayBackError(self):
        drp.setPauseState(True)
        drp.updatePresence()

    def onPlayBackSeek(self, *args):
        drp.updatePresence()

    def onPlayBackSeekChapter(self, *args):
        drp.updatePresence()

    def onPlayBackStarted(self):
        drp.setPauseState(False)
        # media might not be loaded
        drp.updatePresence()

    def onPlayBackStopped(self):
        drp.setPauseState(True)
        drp.updatePresence()


class MyMonitor(xbmc.Monitor):
    def __init__(self):
        xbmc.Monitor.__init__(self)
        log("Monitor initialized")

    def onSettingsChanged(self):
        drp.updateSettings()
        drp.updatePresence()

AVAIABLE_IMAGES = []

try:
    AVAIABLE_IMAGES = json.loads(requests.get("https://hiumee.github.io/kodi/custom.json").text)
except Exception:
    pass


client = None

def handle_client(conn, addr):
    try:
        connected = True
        while connected:
            msg = conn.recv(1024).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            print(f"[{addr}] {msg}")
            conn.close()
            global client
            client = None
    except:
        pass


def start():
    global running
    running = True
    server.listen()
    xbmc.log(f"[LISTENING] Server is listening on {SERVER}")
    global client
    while running:
        try:
            conn, addr = server.accept()
            client = conn
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
        except:
            server.close()

server_Thread = threading.Thread(target=start, args=())
server_Thread.start()

monitor = MyMonitor()
player = MyPlayer()

drp = ServiceRichPresence()
drp.updatePresence()
drp.mainLoop()
