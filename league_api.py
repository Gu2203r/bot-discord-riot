from dotenv import load_dotenv
import os

import requests

load_dotenv()
api_key = os.environ.get("riot_api_key")

def getPuuid(nome, tag):
    link = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{nome}/{tag}?api_key={api_key}"

    response = requests.get(link)

    print(response)

    if response.ok:
        puuid = response.json()["puuid"]

        return puuid
    else:
        return False
    
    

def getElo(puuid):

    link = f"https://br1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}?api_key={api_key}"

    response = requests.get(link)

    print(response)

    if response.ok:

        jsonResp = response.json()
        
        for i in jsonResp:
            if i["queueType"] == "RANKED_SOLO_5x5":
                return i
            
        return None
    else:
        print("Erro ao fazer a requisicao na api da riot")