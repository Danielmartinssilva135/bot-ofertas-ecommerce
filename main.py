import os
import re
import html
import requests
import xml.etree.ElementTree as ET

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
HISTORICO_FILE = "ofertas_enviadas.txt"

def carregar_enviados():
    if not os.path.exists(HISTORICO_FILE):
        return set()
    with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def salvar_enviado(link):
    with open(HISTORICO_FILE, "a", encoding="utf-8") as f:
        f.write(f"{link}\n")

def limpar_texto(texto):
    if not texto:
        return ""
    limpo = re.sub(r"<[^>]+>", "", texto)
    return html.unescape(limpo).strip()

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code != 200:
            print(f"Erro Telegram ({response.status_code}): {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro na ligação ao Telegram: {e}")
        return False

def obter_ofertas():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
    }
    # Feed oficial e aberto de achados/promoções do Tecnoblog
    feed_url = "https://tecnoblog.net/achados/feed/"
    try:
        res = requests.get(feed_url, headers=headers, timeout=20)
        if res.status_code != 200:
            print(f"Falha ao aceder ao feed: status {res.status_code}")
            return []

        root = ET.fromstring(res.content)
        itens = []
        for item in root.findall(".//item"):
            titulo = item.find("title").text if item.find("title") is not None else ""
            link = item.find("link").text if item.find("link") is not None else ""
            descricao = item.find("description").text if item.find("description") is not None else ""

            if link and titulo:
                desc_resumo = limpar_texto(descricao)
                if len(desc_resumo) > 250:
                    desc_resumo = desc_resumo[:250] + "..."

                itens.append({
                    "id": link.strip(),
                    "titulo": limpar_texto(titulo),
                    "link": link.strip(),
                    "descricao": desc_resumo
                })
        return itens
    except Exception as e:
        print(f"Erro ao processar RSS: {e}")
        return []

def executar():
    print("Iniciando varredura de ofertas...")
    enviados = carregar_enviados()
    ofertas = obter_ofertas()

    if not ofertas:
        print("Nenhuma oferta encontrada na fonte.")
        return

    novas_ofertas = 0
    # Envia as 3 primeiras ofertas novas encontradas
    for item in ofertas[:3]:
        identificador = item["id"]
        if identificador in enviados:
            continue

        titulo = html.escape(item["titulo"])
        desc = html.escape(item["descricao"])

        mensagem = (
            f"🔥 <b>ACHADO EM PROMOÇÃO</b>\n\n"
            f"📦 <b>{titulo}</b>\n\n"
            f"📝 {desc}\n\n"
            f"🛒 <a href='{item['link']}'>Ver Oferta Completa</a>"
        )

        if enviar_telegram(mensagem):
            salvar_enviado(identificador)
            novas_ofertas += 1
            print(f"Oferta enviada: {item['titulo']}")

    print(f"Execução finalizada. Total de novas ofertas enviadas: {novas_ofertas}")

if __name__ == "__main__":
    executar()
