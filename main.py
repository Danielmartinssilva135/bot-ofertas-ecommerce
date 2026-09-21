import os
import html
import requests
from urllib.parse import quote_plus

# Credenciais e IDs oficiais
TELEGRAM_TOKEN = "8633628956:AAEub3LFY8SCmkgq8FSbghoaT_hmI73ixnM"
TELEGRAM_CHAT_ID = "@superofertas_brasil2026"
AMAZON_TAG = "superofer0fb9-20"
HISTORICO_FILE = "ofertas_enviadas.txt"

# Lista de termos e departamentos com alto volume de vendas diárias
TERMOS_BUSCA = [
    "Echo Dot Alexa",
    "Kindle 11ª geração",
    "Fire TV Stick 4K",
    "Smartphone Samsung Galaxy",
    "PlayStation 5 Controle DualSense",
    "Fritadeira Air Fryer Mondial",
    "Fone de Ouvido Bluetooth JBL",
    "Smartwatch Relógio Inteligente",
    "Smart TV 50 4K",
    "Robô Aspirador de Pó"
]

def carregar_enviados():
    if not os.path.exists(HISTORICO_FILE):
        return set()
    with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def salvar_enviado(item_id):
    with open(HISTORICO_FILE, "a", encoding="utf-8") as f:
        f.write(f"{item_id}\n")

def gerar_link_afiliado_amazon(termo_busca):
    termo_codificado = quote_plus(termo_busca)
    return f"https://www.amazon.com.br/s?k={termo_codificado}&tag={AMAZON_TAG}"

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
        print(f"Erro no envio: {e}")
        return False

def executar():
    print("Iniciando envio de ofertas verificadas da Amazon...")
    enviados = carregar_enviados()
    enviadas_agora = 0

    for termo in TERMOS_BUSCA:
        if enviadas_agora >= 2:
            break

        if termo in enviados:
            continue

        link_afiliado = gerar_link_afiliado_amazon(termo)
        termo_formatado = html.escape(termo)

        mensagem = (
            f"🔥 <b>OFERTA EXCLUSIVA NA AMAZON BRASIL</b>\n\n"
            f"📦 <b>Produto:</b> {termo_formatado}\n"
            f"🚚 Frete Grátis com Amazon Prime\n"
            f"💳 Parcelamento sem juros disponível\n\n"
            f"🛒 <a href='{link_afiliado}'>Aproveitar Desconto na Amazon</a>"
        )

        if enviar_telegram(mensagem):
            salvar_enviado(termo)
            enviadas_agora += 1
            print(f"Oferta enviada com tag de afiliado: {termo}")

    print(f"Execução concluída. Total de novas postagens: {enviadas_agora}")

if __name__ == "__main__":
    executar()
