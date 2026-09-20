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

def salvar_enviado(identificador):
    with open(HISTORICO_FILE, "a", encoding="utf-8") as f:
        f.write(f"{identificador}\n")

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
        print(f"Resposta Telegram ({response.status_code}): {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro na ligação ao Telegram: {e}")
        return False

def obter_ofertas_exemplo():
    # Fonte local garantida para validação inicial de entrega
    return [
        {
            "id": "oferta_teste_01",
            "titulo": "Smart TV 50 Polegadas 4K UHD",
            "preco": "R$ 1.899,00",
            "loja": "Amazon",
            "link": "https://www.amazon.com.br"
        },
        {
            "id": "oferta_teste_02",
            "titulo": "Smartphone 128GB 5G 8GB RAM",
            "preco": "R$ 1.199,00",
            "loja": "Mercado Livre",
            "link": "https://www.mercadolivre.com.br"
        }
    ]

def executar():
    print("Iniciando varredura de ofertas...")
    enviados = carregar_enviados()
    ofertas = obter_ofertas_exemplo()

    novas_ofertas = 0
    for item in ofertas:
        if item["id"] in enviados:
            continue

        titulo = html.escape(item["titulo"])
        preco = html.escape(item["preco"])
        loja = html.escape(item["loja"])

        mensagem = (
            f"🔥 <b>OFERTA EM DESTAQUE</b>\n\n"
            f"📦 <b>Produto:</b> {titulo}\n"
            f"💰 <b>Preço:</b> {preco}\n"
            f"🏬 <b>Loja:</b> {loja}\n\n"
            f"🛒 <a href='{item['link']}'>Ver Oferta no Site</a>"
        )

        if enviar_telegram(mensagem):
            salvar_enviado(item["id"])
            novas_ofertas += 1
            print(f"Oferta enviada: {item['titulo']}")

    print(f"Execução finalizada. Total de novas ofertas enviadas: {novas_ofertas}")

if __name__ == "__main__":
    executar()
