import os
import re
import random
import time
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# Configurações de ambiente
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
}

def normalizar_link(link):
    """Remove parâmetros de URL, query strings e barras finais para comparação exata."""
    if not link:
        return ""
    link_limpo = link.strip()
    try:
        parsed = urlparse(link_limpo)
        # Mantém apenas esquema, domínio e caminho base
        base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
        return base.lower()
    except Exception:
        return link_limpo.rstrip("/").lower()

def enviar_telegram(texto, imagem_url=None):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(">>> [TELEGRAM] Credenciais ausentes no ambiente.", flush=True)
        return False

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

def carregar_historico_normalizado(caminho):
    linhas = carregar_linhas(caminho)
    return set(normalizar_link(l) for l in linhas if l)

def salvar_historico(caminho, item_original):
    norm = normalizar_link(item_original)
    with open(caminho, "a", encoding="utf-8") as f:
        f.write(f"{norm}\n")

def processar_item(linha, loja_nome, emoji_loja):
    partes = [p.strip() for p in linha.split("|")]
    link = partes[0]
    titulo = partes[1] if len(partes) > 1 else None
    preco_de = partes[2] if len(partes) > 2 else None
    preco_por = partes[3] if len(partes) > 3 else None
    imagem = None

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
        titulo = f"Destaque Especial na {loja_nome}"

    titulo = re.sub(r"\s+", " ", titulo)[:110].strip()

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
        linhas_msg.append("✨ *Promoção com cupons e frete reduzido!*")

    linhas_msg.extend([
        "",
        "🎟️ *Aproveite os cupons de desconto direto no app!*",
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
        historico = carregar_historico_normalizado(loja["historico_file"])

        # Filtra apenas itens cujo link limpo nunca foi postado
        disponiveis = [
            p for p in produtos 
            if normalizar_link(p.split("|")[0]) not in historico
        ]

        if not disponiveis:
            print(f">>> [{loja['nome']}] Sem novos produtos (todos os {len(produtos)} já foram enviados).", flush=True)
            continue

        escolhido = random.choice(disponiveis)
        msg, img, link_original = processar_item(escolhido, loja["nome"], loja["emoji"])

        print(f">>> [{loja['nome']}] Enviando: {link_original}", flush=True)
        if enviar_telegram(msg, img):
            salvar_historico(loja["historico_file"], link_original)
            total_publicados += 1
            time.sleep(3)
        else:
            print(f">>> [{loja['nome']}] Falha no disparo para o Telegram.", flush=True)

    print(f">>> [FIM] Rodada finalizada. Ofertas novas enviadas: {total_publicados}", flush=True)

if __name__ == "__main__":
    rodar_rodada()
