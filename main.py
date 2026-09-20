import os
import re
import html
import requests
from bs4 import BeautifulSoup

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
        print(f"Erro ao enviar para o Telegram: {e}")
        return False

def extrair_ofertas_feed():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    # Canal agregador aberto de promoções nacionais (Amazon, Shopee, Mercado Livre, Magalu, etc.)
    url = "https://t.me/s/LinksBrazil"
    
    try:
        res = requests.get(url, headers=headers, timeout=20)
        if res.status_code != 200:
            print(f"Erro ao carregar ofertas: status {res.status_code}")
            return []
        
        soup = BeautifulSoup(res.text, "html.parser")
        mensagens = soup.find_all("div", class_="tgme_widget_message_wrap")
        
        ofertas = []
        for wrap in mensagens:
            msg_div = wrap.find("div", class_="tgme_widget_message_text")
            if not msg_div:
                continue
            
            links = [a.get("href") for a in msg_div.find_all("a") if a.get("href")]
            # Filtra ofertas que possuam link externo de compra
            links_compra = [l for l in links if "t.me" not in l]
            
            texto = msg_div.get_text(separator="\n").strip()
            
            if links_compra and len(texto) > 15:
                ofertas.append({
                    "id": links_compra[0],
                    "texto": texto,
                    "link": links_compra[0]
                })
        return ofertas
    except Exception as e:
        print(f"Erro na extração de ofertas: {e}")
        return []

def executar():
    print("Iniciando varredura de ofertas...")
    enviados = carregar_enviados()
    ofertas = extrair_ofertas_feed()
    
    if not ofertas:
        print("Nenhuma oferta encontrada na fonte.")
        return

    novas_ofertas = 0
    # Processa as ofertas mais recentes (limite de até 5 por ciclo para não sobrecarregar)
    for item in ofertas[-5:]:
        identificador = item["id"]
        if identificador in enviados:
            continue

        texto_limpo = html.escape(item["texto"])
        if len(texto_limpo) > 600:
            texto_limpo = texto_limpo[:600] + "..."

        mensagem = (
            f"🔥 <b>OFERTA IMPERDÍVEL</b>\n\n"
            f"{texto_limpo}\n\n"
            f"🛒 <a href='{item['link']}'>Acessar Oferta com Desconto</a>"
        )

        sucesso = enviar_telegram(mensagem)
        if sucesso:
            salvar_enviado(identificador)
            novas_ofertas += 1
            print(f"Oferta enviada: {item['link']}")

    print(f"Execução finalizada. Total de novas ofertas enviadas: {novas_ofertas}")

if __name__ == "__main__":
    executar()
