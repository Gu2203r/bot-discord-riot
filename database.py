import pymongo
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

client = pymongo.MongoClient(os.getenv("mongodb_token"))
banco_dados = client["bot_db"]
usuarios = banco_dados["usuarios"]
historico = banco_dados["historico"]
palpites = banco_dados["palpites"]

async def novo_usuario(usuario, riot_puuid):
    filtro = {"discord_id":usuario.id}

    if usuarios.count_documents(filtro) == 0:
        objeto = {
            "discord_id":usuario.id,
            "moedas":100,
            "riot_puuid": riot_puuid
        }
        usuarios.insert_one(objeto)

        return objeto
    else:
        return False
    
async def get_usuario_puuid(usuario):
    filtro = {"discord_id":usuario.id}

    if usuarios.count_documents(filtro) != 0:
        
        resultado = usuarios.find(filtro)

        return resultado.__getitem__(0)["riot_puuid"]
        


    
# Funcao que retorna o salto atual do usuario
async def get_saldo(usuario):
    filtro = {"discord_id":usuario.id}

    if usuarios.count_documents(filtro) != 0:

        resultado = usuarios.find(filtro)

        return resultado.__getitem__(0)["moedas"]
    else:
        return False


async def alterar_saldo(usuario, quantidade):

    moedas_atuais = await get_saldo(usuario)

    filtro = {"discord_id":usuario.id}
    relacao = {"$set": {
        "moedas": moedas_atuais + quantidade
    }}

    usuarios.update_one(filtro, relacao)

    return moedas_atuais + quantidade

async def atualizar_historico(infos_conta):
    hist = {
        "data": datetime.now(),
        "tier": infos_conta["tier"],
        "rank": infos_conta["rank"],
        "league_points": infos_conta["leaguePoints"],
        "wins": infos_conta["wins"],
        "losses": infos_conta["losses"]
    }

    historico.insert_one(hist)

    return hist


async def novo_palpite(usuario, valor_palpite, num_jogos, wins):
    filtro = {"discord_id" : usuario.id}

    if palpites.count_documents(filtro) == 0:
        palpite = {
            "discord_id":usuario.id,
            "valor_palpite":valor_palpite,
            "num_jogos": num_jogos,
            "wins" : wins
        }
        palpites.insert_one(palpite)

        await alterar_saldo(usuario, -valor_palpite)

        return palpite
    else:
        return False
    
async def get_palpite(usuario):
    filtro = {"discord_id" : usuario.id}

    if palpites.count_documents(filtro) != 0:
        palpite = palpites.find(filtro)

        return palpite.__getitem__(0)
    else:
        return False

# retorna o novo saldo se ganhou, 0 se perdeu e False se o palpite nao existe
async def resgatar_palpite(usuario, win):
    filtro = {"discord_id" : usuario.id}

    if palpites.count_documents(filtro) != 0:
        palpite = palpites.find(filtro)
        valor = palpite.__getitem__(0)["valor_palpite"]

        palpites.delete_one(filtro)

        if win:
            return await alterar_saldo(usuario, valor * 2)

        return 0

    else:
        return False

