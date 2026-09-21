import os
import re
import html
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

TELEGRAM_TOKEN = "8633628956:AAEub3LFY8SCmkgq8FSbghoaT_hmI73ixnM"
TELEGRAM_CHAT_ID = "@superofertas_brasil2026"
AMAZON_TAG = "superofer0fb9-20"
HISTORICO_FILE = "ofertas_enviadas.txt"

def carregar_enviados():
    if not os.path.exists(HISTORICO_FILE):
        return set()
    with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def salvar_enviado(link):
    with open(HISTORICO_FILE, "a", encoding="utf-8") as f:
        f.write(f"{link}\n")

def limpar_html(texto):
    if not texto:
        return ""
    limpo = re.sub(r"<[^>]+>", "", texto)
    return html.unescape(limpo).strip()

def aplicar_tag_afiliado(url):
    """Garante a inclusão da sua tag se for link da Amazon."""
    try:
        parsed = urlparse(url)
        if "amazon.com" in parsed.netloc:
            queries = parse_qs(parsed.query)
            queries["tag"] = [AMAZON_TAG]
            nova_query = urlencode(queries, doseq=True)
            return urlunparse(parsed._replace(query=nova_query))
    except Exception:
        pass
    return url

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        res = requests.post(url, json=payload, timeout=15)
        return res.status_code == 200
    except Exception as e:
        print(f"Erro Telegram: {e}")
        return False

def recolher_ofertas():
    feed_url = "https://news.google.com/rss/search?q=oferta+desconto+amazon+brasil&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        resposta = requests.get(feed_url, headers=headers, timeout=20)
        if resposta.status_code != 200:
            return []

        root = ET.fromstring(resposta.content)
        itens = []
        for el in root.findall(".//item"):
            titulo = el.find("title").text if el.find("title") is not None else ""
            link = el.find("link").text if el.find("link") is not None else ""

            if titulo and link:
                itens.append({
                    "id": link.strip(),
                    "titulo": limpar_html(titulo),
                    "link": aplicar_tag_afiliado(link.strip())
                })
        return itens
    except Exception as e:
        print(f"Erro no feed: {e}")
        return []

def executar():
    print("A pesquisar ofertas com links monetizados...")
    enviados = carregar_enviados()
    ofertas = recolher_ofertas()

    if not ofertas:
        print("Nenhuma oferta nova encontrada.")
        return

    enviadas = 0
    for item in ofertas:
        if enviadas >= 2:
            break

        if item["id"] in enviados:
            continue

        titulo = html.escape(item["titulo"])

        mensagem = (
            f"🔥 <b>OFERTA DO DIA RECOMENDADA</b>\n\n"
            f"📦 <b>{titulo}</b>\n\n"
            f"🛒 <a href='{item['link']}'>Conferir Desconto na Loja</a>"
        )

        if enviar_telegram(mensagem):
            salvar_enviado(item["id"])
            enviadas += 1
            print(f"Enviada: {item['titulo']}")

    print(f"Total enviadas nesta ronda: {enviadas}")

if __name__ == "__main__":
    executar()
