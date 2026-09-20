import os
import html
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
        print(f"Erro ao enviar para Telegram: {e}")
        return False

def obter_ofertas():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    # Endpoint JSON público de ofertas recentes do Pelando
    url = "https://www.pelando.com.br/api/v2/deals?page=1&limit=15&tab=hot"
    
    try:
        res = requests.get(url, headers=headers, timeout=20)
        if res.status_code != 200:
            print(f"Falha na API: status {res.status_code}")
            return []
            
        dados = res.json()
        itens = []
        for deal in dados.get("deals", []):
            titulo = deal.get("title", "")
            preco = deal.get("price", "")
            cupom = deal.get("couponCode", "")
            link_loja = deal.get("link", "") or deal.get("sourceUrl", "")
            slug = deal.get("slug", "")
            link_final = link_loja if link_loja else f"https://www.pelando.com.br/d/{slug}"
            
            if titulo and link_final:
                itens.append({
                    "id": str(deal.get("id", link_final)),
                    "titulo": titulo,
                    "preco": f"R$ {preco}" if preco else "Confira na loja",
                    "cupom": cupom,
                    "link": link_final
                })
        return itens
    except Exception as e:
        print(f"Erro ao obter ofertas JSON: {e}")
        return []

def executar():
    print("Iniciando varredura de ofertas...")
    enviados = carregar_enviados()
    ofertas = obter_ofertas()
    
    if not ofertas:
        print("Nenhuma oferta encontrada na API.")
        return

    novas_ofertas = 0
    # Envia as 3 primeiras promoções novas
    for item in ofertas[:3]:
        identificador = item["id"]
        if identificador in enviados:
            continue

        titulo = html.escape(item["titulo"])
        preco = html.escape(item["preco"])
        cupom_txt = f"\n🎟️ <b>Cupão:</b> <code>{item['cupom']}</code>" if item["cupom"] else ""

        mensagem = (
            f"🔥 <b>SUPER OFERTA ENCONTRADA</b>\n\n"
            f"📦 <b>{titulo}</b>\n\n"
            f"💰 <b>Preço:</b> {preco}{cupom_txt}\n\n"
            f"🛒 <a href='{item['link']}'>Aproveitar Desconto</a>"
        )

        if enviar_telegram(mensagem):
            salvar_enviado(identificador)
            novas_ofertas += 1
            print(f"Oferta enviada: {item['titulo']}")

    print(f"Execução finalizada. Total de novas ofertas enviadas: {novas_ofertas}")

if __name__ == "__main__":
    executar()
