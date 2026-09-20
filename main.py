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

def limpar_html(texto):
    if not texto:
        return ""
    clean = re.sub(r"<.*?>", "", texto)
    return html.unescape(clean).strip()

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
        print(f"Erro na conexao com o Telegram: {e}")
        return False

def obter_ofertas():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    feed_url = "https://www.promobit.com.br/feed/"
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
                itens.append({
                    "titulo": limpar_html(titulo),
                    "link": link.strip(),
                    "descricao": limpar_html(descricao)[:200]
                })
        return itens
    except Exception as e:
        print(f"Erro ao analisar RSS: {e}")
        return []

def executar():
    print("Iniciando varredura de ofertas...")
    enviados = carregar_enviados()
    ofertas = obter_ofertas()

    if not ofertas:
        print("Nenhuma oferta encontrada no feed.")
        return

    novas_ofertas = 0
    # Envia ate 3 ofertas novas por lote para inicializar o canal
    for item in ofertas[:3]:
        link = item["link"]
        if link in enviados:
            continue

        mensagem = (
            f"🔥 <b>OFERTA DETECTADA</b>\n\n"
            f"📦 <b>Produto:</b> {item['titulo']}\n\n"
            f"📝 <b>Resumo:</b> {item['descricao']}...\n\n"
            f"🔗 <a href='{link}'>Ver detalhes e comprar</a>"
        )

        if enviar_telegram(mensagem):
            salvar_enviado(link)
            novas_ofertas += 1
            print(f"Oferta enviada: {item['titulo']}")

    print(f"Execução finalizada. Total de novas ofertas enviadas: {novas_ofertas}")

if __name__ == "__main__":
    executar()
