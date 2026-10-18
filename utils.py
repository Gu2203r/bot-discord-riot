import discord


COR_PRINCIPAL = 0x32D583
COR_ERRO = 0xEF4444
COR_ALERTA = 0xF59E0B
COR_INFO = 0x38BDF8
COR_SUCESSO = 0x22C55E


def criar_embed(titulo, descricao=None, cor=COR_PRINCIPAL):
    embed = discord.Embed(
        title=titulo,
        description=descricao,
        color=cor
    )
    embed.set_footer(text="Zwhopper | League of Legends")
    return embed


def embed_sucesso(titulo, descricao):
    return criar_embed(titulo, descricao, COR_SUCESSO)


def embed_erro(titulo, descricao):
    return criar_embed(titulo, descricao, COR_ERRO)


def embed_alerta(titulo, descricao):
    return criar_embed(titulo, descricao, COR_ALERTA)


def formatar_moedas(valor):
    return f"{valor:,}".replace(",", ".")


def formatar_winrate(wins, losses):
    total = wins + losses
    if total == 0:
        return "0.0%"

    return f"{(wins / total) * 100:.1f}%"


def criar_embed_elo(nome, dados_elo):
    rank_player = dados_elo["tier"]
    wins = dados_elo["wins"]
    losses = dados_elo["losses"]
    total = wins + losses

    embed = criar_embed(
        f"Elo de {nome}",
        "Resumo atual da fila ranqueada solo/duo.",
        COR_PRINCIPAL
    )
    embed.set_thumbnail(url=getUrlIconElo(rank_player))
    embed.add_field(
        name="Liga",
        value=f"**{rank_player} {dados_elo['rank']}**\n{dados_elo['leaguePoints']} PDL",
        inline=False
    )
    embed.add_field(name="Vitórias", value=str(wins), inline=True)
    embed.add_field(name="Derrotas", value=str(losses), inline=True)
    embed.add_field(name="Partidas", value=str(total), inline=True)
    embed.add_field(name="Win rate", value=formatar_winrate(wins, losses), inline=False)

    return embed


def getUrlIconElo(elo):
    if elo == "IRON":
        return "https://opgg-static.akamaized.net/images/medals_mini/iron.png?image=q_auto:good,f_webp,w_48&v=1782977085"

    elif elo == "BRONZE":
        return "https://opgg-static.akamaized.net/images/medals_mini/bronze.png?image=q_auto:good,f_webp,w_48&v=1782977085"

    elif elo == "SILVER":
        return "https://opgg-static.akamaized.net/images/medals_mini/silver.png?image=q_auto:good,f_webp,w_48&v=1782977085"

    elif elo == "GOLD":
        return "https://opgg-static.akamaized.net/images/medals_mini/gold.png?image=q_auto:good,f_webp,w_48&v=1782977085"

    elif elo == "PLATINUM":
        return "https://opgg-static.akamaized.net/images/medals_mini/platinum.png?image=q_auto:good,f_webp,w_48&v=1782977085"

    elif elo == "EMERALD":
        return "https://opgg-static.akamaized.net/images/medals_mini/emerald.png?image=q_auto:good,f_webp,w_48&v=1782977085"

    elif elo == "DIAMOND":
        return "https://opgg-static.akamaized.net/images/medals_mini/diamond.png?image=q_auto:good,f_webp,w_48&v=1782977085"

    elif elo == "MASTER":
        return "https://opgg-static.akamaized.net/images/medals_mini/master.png?image=q_auto:good,f_webp,w_48&v=1782977085"

    elif elo == "GRANDMASTER":
        return "https://opgg-static.akamaized.net/images/medals_mini/grandmaster.png?image=q_auto:good,f_webp,w_48&v=1782977085"

    elif elo == "CHALLENGER":
        return "https://opgg-static.akamaized.net/images/medals_mini/challenger.png?image=q_auto:good,f_webp,w_48&v=1782977085"

    return None
