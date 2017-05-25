# -*- coding: utf-8 -*-
from wox import Wox, WoxAPI
import re
import os, sys, glob
import json
import urllib
import urllib.request
import requests
from bs4 import BeautifulSoup


class Steamlauncher(Wox):

    gameList = []
    f = open('./config.json', 'r')
    dirConfig = json.load(f)
    f.close()

    if not dirConfig["steam_dir"]:
        steamDir = None
    else:
        if os.path.isdir(dirConfig['steam_dir']) and os.path.isfile(dirConfig['steam_dir'] + 'steam.exe'):
            steamDir = dirConfig["steam_dir"]
        else:
            steamDir = False

    if not dirConfig["steamapps_dir"]:
        steamappsDir = None
    else:
        if os.path.isdir(dirConfig['steamapps_dir']) and not not glob.glob(dirConfig['steamapps_dir'] + 'appmanifest_*.acf'):
            steamappsDir = dirConfig["steamapps_dir"]
            acfList = glob.glob(dirConfig['steamapps_dir'] + 'appmanifest_*.acf')
            for line in acfList:
                gameId = re.search(r"[0-9]+", line)
                gameId = gameId.group()
                f = open(line, 'r')
                for line in f:
                    if line.find("name") >= 0:
                        gameTitle = line.strip('\n')
                        gameTitle = gameTitle[9:].strip('"')
                        break
                f.close()
                if os.path.isfile('./icon/' + gameId + '.jpg'):
                    gameIcon = './icon/'+ gameId + '.jpg'
                else:
                    try:
                        url = 'https://steamdb.info/app/{}/'.format(gameId)
                        r = requests.get(url)
                        soup = BeautifulSoup(r.text, "html.parser")
                        data = soup.find('img', attrs={'class':'app-icon avatar'})
                        img = data.attrs['src']
                        urllib.request.urlretrieve(img, './icon/' + gameId + '.jpg')
                        gameIcon = './icon/'+ gameId + '.jpg'
                    except Exception as e:
                        gameIcon = './icon/missing.png'
                gameList.append({'gameId':gameId, 'gameTitle':gameTitle, 'gameIcon':gameIcon})

        else:
            steamappsDir = False

    def query(self, query):
        result = []
        steamDir = self.steamDir
        steamappsDir = self.steamappsDir
        gameList = self.gameList

        if not query and steamDir is not None and steamDir is not False and steamappsDir is not None and steamappsDir is not False:
            for line in gameList:
                result.append({
                    "Title": line['gameTitle'] + " - ({})".format(line['gameId']),
                    "SubTitle": "Press Enter key to launch '{}'.".format(line['gameTitle']),
                    "IcoPath": line['gameIcon'],
                    "JsonRPCAction": {
                        "method": "launchGame",
                        "parameters": [line['gameId']],
                        "dontHideAfterAction": False
                    }
                })
            return result

        if steamDir is not None and steamDir is not False and steamappsDir is not None and steamappsDir is not False:
            for line in gameList:
                if re.match(query.upper(), line['gameTitle'].upper()):
                    result.append({
                        "Title": line['gameTitle'] + " - ({})".format(line['gameId']),
                        "SubTitle": "Press Enter key to launch '{}'.".format(line['gameTitle']),
                        "IcoPath": line['gameIcon'],
                        "JsonRPCAction": {
                            "method": "launchGame",
                            "parameters": [line['gameId']],
                            "dontHideAfterAction": False
                        }
                    })
            if not result:
                result.append({
                    "Title": "Can't find '{}'.".format(query),
                    "SubTitle": "Please check game has been installed correctly.",
                    "IcoPath": "icon/launcher.png",
                })
            return result

        if steamDir is None:
            result.append({
                "Title": "Can't find Steam Directory.",
                "SubTitle": "Please add Steam Path:'{}'".format(query),
                "IcoPath": "icon/launcher.png",
                "JsonRPCAction": {
                    "method": "saveSteamDirectory",
                    "parameters": [query],
                    "dontHideAfterAction": True
                }
            })

        if steamappsDir is None:
            result.append({
                "Title": "Can't find Steamapps Directory.",
                "SubTitle": "Please add Steamapps Path:'{}'".format(query),
                "IcoPath": "icon/launcher.png",
                "JsonRPCAction": {
                    "method": "saveSteamAppsDirectory",
                    "parameters": [query],
                    "dontHideAfterAction": True
                }
            })

        if steamDir is False:
            result.append({
                "Title": "Steam path is invalid.",
                "SubTitle": "Try add Steam Path again:'{}'".format(query),
                "IcoPath": "icon/launcher.png",
                "JsonRPCAction": {
                    "method": "saveSteamDirectory",
                    "parameters": [query],
                    "dontHideAfterAction": True
                }
            })

        if steamappsDir is False:
            result.append({
                "Title": "Steamapps path is invalid.",
                "SubTitle": "Try add Steamapps Path again:'{}'".format(query),
                "IcoPath": "icon/launcher.png",
                "JsonRPCAction": {
                    "method": "saveSteamAppsDirectory",
                    "parameters": [query],
                    "dontHideAfterAction": True
                }
            })
        return result

    def saveSteamDirectory(self, path):
        dirConfig = self.dirConfig
        dirConfig['steam_dir'] = re.sub(r'[/\\]+', '/', path.rstrip('/\\')) + '/'
        f = open('./config.json', 'w')
        json.dump(dirConfig, f, indent=4)
        f.close()
        WoxAPI.show_msg("Steam directory path has been saved", dirConfig['steam_dir'])

    def saveSteamAppsDirectory(self, path):
        dirConfig = self.dirConfig
        dirConfig['steamapps_dir'] = re.sub(r'[/\\]+', '/', path.rstrip('/\\')) + '/'
        f = open('./config.json', 'w')
        json.dump(dirConfig, f, indent=4)
        f.close()
        WoxAPI.show_msg("Steam apps directory path has been saved", dirConfig['steamapps_dir'])

    def launchGame(self, gameId):
        steamDir = self.steamDir
        gamePath = '"{}steam.exe"'.format(steamDir) + " -applaunch {}".format(gameId)
        os.system(gamePath)

if __name__ == "__main__":
    Steamlauncher()