import os

import discord
import dotenv
from discord.ext import commands

import league_api
import utils
from database import *

dotenv.load_dotenv()
bot_token = os.environ.get("bot_token")

permissoes = discord.Intents.default()
permissoes.message_content = True
permissoes.members = True
bot = commands.Bot(command_prefix=".", intents=permissoes)


def criar_embed_conta_nao_encontrada():
    return utils.embed_alerta(
        "Conta não cadastrada",
        "Use `/cadastro` com seu nome e tag da Riot antes de apostar ou consultar saldo."
    )


@bot.event
async def on_ready():
    print("O bot está pronto")


@bot.command()
async def sincronizar(ctx: commands.Context):
    if ctx.author.id == 314889410204401665:
        sincs = await bot.tree.sync()
        embed = utils.embed_sucesso(
            "Comandos sincronizados",
            f"{len(sincs)} comandos slash foram atualizados no Discord."
        )
        await ctx.reply(embed=embed)
    else:
        embed = utils.embed_erro(
            "Sem permissão",
            "Você não tem permissão para usar esse comando."
        )
        await ctx.reply(embed=embed)


@bot.tree.command(name="tx-elo", description="Mostra o elo do grande Tx11")
async def verEloTx11(interaction: discord.Interaction):
    jsonElo = league_api.getElo("kKe7SHq0xZ5zDe36tB7UU18gx_4Qv6tHcroTa7ygMUvnR9nZBCIpn0gdcJpbA8_fsSl14e9bpY1V7A")

    if jsonElo is None:
        embed = utils.embed_alerta(
            "Elo não encontrado",
            "Não encontrei dados de ranqueada solo/duo para essa conta agora."
        )
        await interaction.response.send_message(embed=embed)
        return

    await interaction.response.send_message(embed=utils.criar_embed_elo("Tx11", jsonElo))


@bot.tree.command(name="ver-elo", description="Exibe o elo da conta inserida")
async def verElo(interaction: discord.Interaction, nome: str, tag: str):
    puuid = league_api.getPuuid(nome, tag)

    if puuid is False:
        embed = utils.embed_erro(
            "Invocador não encontrado",
            "Confira se o nome e a tag foram digitados corretamente. Exemplo: `/ver-elo nome:Tx11 tag:BR1`."
        )
        await interaction.response.send_message(embed=embed)
        return

    jsonElo = league_api.getElo(puuid)

    if jsonElo is None:
        embed = utils.embed_alerta(
            "Elo não encontrado",
            "Essa conta não possui dados de ranqueada solo/duo no momento."
        )
        await interaction.response.send_message(embed=embed)
        return

    await interaction.response.send_message(embed=utils.criar_embed_elo(nome, jsonElo))


@bot.tree.command(name="cadastro", description="Cadastra o seu usuário com sua conta Riot")
async def cadastro(interaction: discord.Interaction, nome: str, tag: str):
    puuid = league_api.getPuuid(nome, tag)

    if puuid is False:
        embed = utils.embed_erro(
            "Usuário não encontrado",
            "Não consegui encontrar essa conta Riot. Confira o nome e a tag e tente novamente."
        )
        await interaction.response.send_message(embed=embed)
        return

    novo = await novo_usuario(interaction.user, puuid)

    if novo is False:
        embed = utils.embed_alerta(
            "Cadastro já existe",
            "Você já tem uma conta Riot vinculada ao seu usuário do Discord."
        )
        await interaction.response.send_message(embed=embed)
        return

    embed = utils.embed_sucesso(
        "Cadastro concluído",
        f"Sua conta foi vinculada com sucesso. Saldo inicial: **{utils.formatar_moedas(novo['moedas'])} moedas**."
    )
    embed.add_field(name="Conta Riot", value=f"{nome}#{tag}", inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="saldo", description="Veja o seu saldo atual")
async def ver_saldo(interaction: discord.Interaction):
    moedas = await get_saldo(interaction.user)

    if moedas is False:
        await interaction.response.send_message(embed=criar_embed_conta_nao_encontrada())
        return

    embed = utils.criar_embed(
        "Seu saldo",
        f"Você tem **{utils.formatar_moedas(moedas)} moedas** disponíveis para apostar.",
        utils.COR_INFO
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="perfil", description="Mostra seu perfil com o elo da conta Riot vinculada")
async def perfil(interaction: discord.Interaction):
    puuid = await get_usuario_puuid(interaction.user)

    if puuid is None:
        await interaction.response.send_message(embed=criar_embed_conta_nao_encontrada())
        return

    jsonElo = league_api.getElo(puuid)

    if jsonElo is None:
        embed = utils.embed_alerta(
            "Elo não encontrado",
            "Sua conta vinculada não possui dados de ranqueada solo/duo no momento."
        )
        await interaction.response.send_message(embed=embed)
        return

    moedas = await get_saldo(interaction.user)
    embed = utils.criar_embed_elo(interaction.user.display_name, jsonElo)
    embed.title = f"Perfil de {interaction.user.display_name}"

    if moedas is not False:
        embed.add_field(name="Saldo", value=f"{utils.formatar_moedas(moedas)} moedas", inline=False)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="top-moedas", description="Mostra os 5 perfis cadastrados com mais moedas")
async def top_moedas(interaction: discord.Interaction):
    ranking = list(
        usuarios.find(
            {},
            {"discord_id": 1, "moedas": 1, "_id": 0}
        ).sort("moedas", -1).limit(5)
    )

    if len(ranking) == 0:
        embed = utils.embed_alerta(
            "Ranking vazio",
            "Ainda não existe nenhum perfil cadastrado para aparecer no top moedas."
        )
        await interaction.response.send_message(embed=embed)
        return

    embed = utils.criar_embed(
        "Top 5 Perfis com os maiores saldos",
        cor=utils.COR_INFO
    )

    for posicao, perfil_rank in enumerate(ranking, start=1):
        discord_id = perfil_rank["discord_id"]
        moedas = perfil_rank.get("moedas", 0)
        embed.add_field(
            name=f"{posicao}. {await bot.fetch_user(discord_id)}",
            value=f"{utils.formatar_moedas(moedas)} moedas",
            inline=False
        )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="palpite", description="Faça um palpite para sua próxima partida")
async def palpite(interaction: discord.Interaction, valor: int):
    saldo = await get_saldo(interaction.user)

    if saldo is False:
        await interaction.response.send_message(embed=criar_embed_conta_nao_encontrada())
        return

    if valor <= 0:
        embed = utils.embed_alerta(
            "Valor inválido",
            "Escolha uma quantidade de moedas maior que zero para fazer o palpite."
        )
        await interaction.response.send_message(embed=embed)
        return

    if valor > saldo:
        embed = utils.embed_erro(
            "Saldo insuficiente",
            f"Você tem **{utils.formatar_moedas(saldo)} moedas**, mas tentou apostar **{utils.formatar_moedas(valor)}**."
        )
        await interaction.response.send_message(embed=embed)
        return

    puuid = await get_usuario_puuid(interaction.user)
    estado_atual = league_api.getElo(puuid)

    if estado_atual is None:
        embed = utils.embed_alerta(
            "Elo não encontrado",
            "Não consegui ler seus dados de ranqueada solo/duo para registrar o palpite."
        )
        await interaction.response.send_message(embed=embed)
        return

    total_jogos = estado_atual["wins"] + estado_atual["losses"]
    sucesso = await novo_palpite(interaction.user, valor, total_jogos, estado_atual["wins"])

    if sucesso is False:
        embed = utils.embed_alerta(
            "Palpite ativo encontrado",
            "Você já possui um palpite ativo. Resgate o palpite atual antes de criar outro."
        )
        await interaction.response.send_message(embed=embed)
        return

    embed = utils.embed_sucesso(
        "Palpite registrado",
        f"Você apostou **{utils.formatar_moedas(valor)} moedas** na sua próxima partida ranqueada."
    )
    embed.add_field(name="Saldo após aposta", value=f"{utils.formatar_moedas(saldo - valor)} moedas", inline=True)
    embed.add_field(name="Retorno se vencer", value=f"{utils.formatar_moedas(valor * 2)} moedas", inline=True)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="resgatar", description="Resgate o valor do seu último palpite")
async def resgatar(interaction: discord.Interaction):
    palpite_resgatar = await get_palpite(interaction.user)

    if palpite_resgatar is False:
        embed = utils.embed_alerta(
            "Nenhum palpite ativo",
            "Você ainda não tem um palpite para resgatar. Use `/palpite` antes da sua próxima partida."
        )
        await interaction.response.send_message(embed=embed)
        return

    wins_palpite = int(palpite_resgatar["wins"])
    num_jogos_palpite = int(palpite_resgatar["num_jogos"])
    valor_palpite = int(palpite_resgatar["valor_palpite"])

    puuid = await get_usuario_puuid(interaction.user)
    elo_atual = league_api.getElo(puuid)

    if elo_atual is None:
        embed = utils.embed_alerta(
            "Elo não encontrado",
            "Não consegui conferir o resultado da partida agora. Tente novamente em alguns minutos."
        )
        await interaction.response.send_message(embed=embed)
        return

    total_jogos = elo_atual["wins"] + elo_atual["losses"]

    if (wins_palpite + 1) == elo_atual["wins"] and (num_jogos_palpite + 1) == total_jogos:
        novo_saldo = await resgatar_palpite(interaction.user, True)
        embed = utils.embed_sucesso(
            "Palpite vencido",
            f"Boa! Você resgatou **{utils.formatar_moedas(valor_palpite * 2)} moedas**."
        )
        embed.add_field(name="Novo saldo", value=f"{utils.formatar_moedas(novo_saldo)} moedas", inline=False)
        await interaction.response.send_message(embed=embed)
    elif num_jogos_palpite == total_jogos:
        embed = utils.embed_alerta(
            "Partida ainda não computada",
            "Seu jogo ainda não apareceu na Riot. Espere um pouco e tente resgatar novamente."
        )
        await interaction.response.send_message(embed=embed)
    else:
        await resgatar_palpite(interaction.user, False)
        embed = utils.embed_erro(
            "Palpite perdido",
            "Você demorou muito para resgatar seu último palpite, então ele foi perdido."
        )
        await interaction.response.send_message(embed=embed)


@bot.tree.command(name="ola", description="Te responde um ola!")
async def ola(interaction:discord.Interaction):
    await interaction.response.send_message("Olá!")


bot.run(bot_token)



