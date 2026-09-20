import os
import re
import html
import feedparser
import requests

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

def limpar_texto(raw_html):
    clean = re.sub(r'<.*?>', '', raw_html)
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
        return response.status_code == 200
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")
        return False

def executar():
    print("Iniciando varredura de ofertas...")
    enviados = carregar_enviados()
    
    feed_url = "https://www.pelando.com.br/rss/all"
    feed = feedparser.parse(feed_url)
    
    if not feed.entries:
        print("Nenhuma oferta encontrada no momento.")
        return

    novas_ofertas = 0

    for entry in reversed(feed.entries):
        link = entry.get("link", "").strip()
        titulo = entry.get("title", "").strip()
        descricao = limpar_texto(entry.get("summary", ""))
        
        if len(descricao) > 180:
            descricao = descricao[:180] + "..."

        if not link or link in enviados:
            continue

        mensagem = (
            f"🔥 <b>OFERTA DETECTADA</b>\n\n"
            f"📦 <b>Produto:</b> {titulo}\n\n"
            f"📝 <b>Detalhes:</b> {descricao}\n\n"
            f"🔗 <a href='{link}'>Clique aqui para conferir a oferta</a>"
        )

        sucesso = enviar_telegram(mensagem)
        if sucesso:
            salvar_enviado(link)
            novas_ofertas += 1
            print(f"Oferta enviada: {titulo}")

    print(f"Execucao finalizada. Total de novas ofertas enviadas: {novas_ofertas}")

if __name__ == "__main__":
    executar()
