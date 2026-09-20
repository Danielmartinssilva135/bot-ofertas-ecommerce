import os
import re
import html
import requests
import xml.etree.ElementTree as ET

TELEGRAM_TOKEN = "8633628956:AAEub3LFY8SCmkgq8FSbghoaT_hmI73ixnM"
TELEGRAM_CHAT_ID = "@superofertas_brasil2026"
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
        print(f"Telegram status: {res.status_code}")
        return res.status_code == 200
    except Exception as e:
        print(f"Erro Telegram: {e}")
        return False

def recolher_ofertas():
    # Feed RSS oficial de ofertas e descontos no Brasil
    feed_url = "https://news.google.com/rss/search?q=oferta+desconto+promocao+brasil&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        resposta = requests.get(feed_url, headers=headers, timeout=20)
        if resposta.status_code != 200:
            print(f"Erro ao descarregar feed: HTTP {resposta.status_code}")
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
                    "link": link.strip()
                })
        return itens
    except Exception as e:
        print(f"Erro no processamento do feed: {e}")
        return []

def executar():
    print("A pesquisar novas ofertas...")
    enviados = carregar_enviados()
    ofertas = recolher_ofertas()

    if not ofertas:
        print("Nenhuma oferta disponível no momento.")
        return

    enviadas = 0
    # Publica 2 ofertas novas por execução
    for item in ofertas:
        if enviadas >= 2:
            break

        if item["id"] in enviados:
            continue

        titulo = html.escape(item["titulo"])

        mensagem = (
            f"🔥 <b>OFERTA & DESCONTO EM DESTAQUE</b>\n\n"
            f"📦 <b>{titulo}</b>\n\n"
            f"🛒 <a href='{item['link']}'>Ver Oferta Completa</a>"
        )

        if enviar_telegram(mensagem):
            salvar_enviado(item["id"])
            enviadas += 1
            print(f"Publicada com sucesso: {item['titulo']}")

    print(f"Processo concluído. Novas mensagens: {enviadas}")

if __name__ == "__main__":
    executar()
