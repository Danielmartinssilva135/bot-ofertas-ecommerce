import os
import re
import random
import time
import requests
from bs4 import BeautifulSoup

# Configurações de ambiente
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
}

def enviar_telegram(texto, imagem_url=None):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(">>> [TELEGRAM] Credenciais ausentes no ambiente.", flush=True)
        return False

    # Se houver imagem válida, envia com foto
    if imagem_url:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "photo": imagem_url,
            "caption": texto,
            "parse_mode": "Markdown"
        }
        try:
            r = requests.post(url, json=payload, timeout=25)
            if r.status_code == 200:
                return True
        except Exception as e:
            print(f">>> [TELEGRAM] Falha ao enviar foto: {e}", flush=True)

    # Fallback para envio de mensagem de texto normal
    url_msg = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload_msg = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        r = requests.post(url_msg, json=payload_msg, timeout=20)
        return r.status_code == 200
    except Exception as e:
        print(f">>> [TELEGRAM] Erro no envio de texto: {e}", flush=True)
        return False

def carregar_linhas(caminho):
    if not os.path.exists(caminho):
        return []
    with open(caminho, "r", encoding="utf-8") as f:
        return [l.strip() for l in f.readlines() if l.strip() and not l.startswith("#")]

def salvar_historico(caminho, item):
    with open(caminho, "a", encoding="utf-8") as f:
        f.write(f"{item}\n")

def processar_item(linha, loja_nome, emoji_loja):
    """
    Suporta dois formatos na linha:
    1) Link simples: https://shope.ee/...
    2) Detalhado: Link | Nome do Produto | Preco Anterior | Preco Atual
    """
    partes = [p.strip() for p in linha.split("|")]
    link = partes[0]
    titulo = partes[1] if len(partes) > 1 else None
    preco_de = partes[2] if len(partes) > 2 else None
    preco_por = partes[3] if len(partes) > 3 else None
    imagem = None

    # Se não houver título definido, tenta capturar da página
    if not titulo:
        try:
            resp = requests.get(link, headers=HEADERS, timeout=12)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                og_title = soup.find("meta", property="og:title")
                og_image = soup.find("meta", property="og:image")
                
                if og_title and og_title.get("content"):
                    titulo = og_title["content"]
                elif soup.title:
                    titulo = soup.title.string.strip()

                if og_image and og_image.get("content"):
                    imagem = og_image["content"]
        except Exception:
            pass

    if not titulo:
        titulo = f"Produto em Destaque na {loja_nome}"

    # Limpeza de títulos muito longos
    titulo = re.sub(r"\s+", " ", titulo)[:110].strip()

    # Formatação da mensagem com preços visíveis
    linhas_msg = [
        f"{emoji_loja} *ACHADINHO NA {loja_nome.upper()}*",
        "",
        f"📦 *{titulo}*"
    ]

    if preco_de and preco_por:
        linhas_msg.extend([
            f"❌ De: ~R$ {preco_de}~",
            f"🔥 *Por apenas: R$ {preco_por}* com desconto!"
        ])
    elif preco_por:
        linhas_msg.append(f"🔥 *Por apenas: R$ {preco_por}*")
    else:
        linhas_msg.append("✨ *Preço promocional imperdível por tempo limitado!*")

    linhas_msg.extend([
        "",
        "🎟️ *Aproveite os cupons de frete grátis e desconto no app!*",
        "",
        f"[👉 CLIQUE AQUI PARA COMPRAR]({link})"
    ])

    return "\n".join(linhas_msg), imagem, link

def rodar_rodada():
    lojas = [
        {
            "nome": "Shopee",
            "emoji": "🧡",
            "produtos_file": "produtos_shopee.txt",
            "historico_file": "historico_shopee.txt"
        },
        {
            "nome": "Amazon",
            "emoji": "📦",
            "produtos_file": "produtos_amazon.txt",
            "historico_file": "historico_amazon.txt"
        },
        {
            "nome": "Mercado Livre",
            "emoji": "💛",
            "produtos_file": "produtos_mercadolivre.txt",
            "historico_file": "historico_mercadolivre.txt"
        }
    ]

    total_publicados = 0

    for loja in lojas:
        produtos = carregar_linhas(loja["produtos_file"])
        historico = set(carregar_linhas(loja["historico_file"]))

        disponiveis = [p for p in produtos if p.split("|")[0].strip() not in historico]

        if not disponiveis:
            print(f">>> [{loja['nome']}] Sem novos produtos para postar ou lista esgotada.", flush=True)
            continue

        # Seleciona um produto pendente
        escolhido = random.choice(disponiveis)
        msg, img, link_base = processar_item(escolhido, loja["nome"],
