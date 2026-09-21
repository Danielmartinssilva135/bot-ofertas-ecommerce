import os
import html
import requests
from urllib.parse import quote_plus

# Credenciais e configurações
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8633628956:AAEub3LFY8SCmkgq8FSbghoaT_hmI73ixnM")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "@superofertas_brasil2026")
AMAZON_TAG = os.environ.get("AMAZON_TAG", "superofer0fb9-20")

ARQUIVO_PRODUTOS_ML = "produtos_mercadolivre.txt"
HISTORICO_AMAZON = "historico_amazon.txt"
HISTORICO_ML = "historico_mercadolivre.txt"

TERMOS_AMAZON = [
    "Bolsa Térmica Marmita Almoço Trabalho",
    "Lancheira Térmica Impermeável Fitness",
    "Bolsa Térmica 2 Compartimentos Marmiteira",
    "Kit Bolsa Térmica com Potes de Vidro Herméticos",
    "Bolsa Térmica Everbags Master",
    "Marmita Elétrica Portátil Bivolt Automóvel e Tomada",
    "Pote Térmico Inox para Sopas e Refeições Quentes",
    "Caminha para Cachorro Confortável Lavável",
    "Fonte de Água para Gatos e Cães Automática",
    "Brinquedo Interativo Mordedor Pet",
    "Tapete Higiênico para Cães",
    "Comedouro e Bebedouro Elevado Inox Pet",
    "Escova Rasqueadeira Tira Pelos Pet",
    "Arranhador para Gatos com Brinquedo",
    "Bolsa Mochila de Transporte Pet Astronauta",
    "Bolsa Feminina Transversal",
    "Bolsa Feminina de Ombro Chenson",
    "Protetor Solar Facial La Roche-Posay",
    "Escova Secadora Taiff",
    "Organizador de Maquiagem Acrílico",
    "Jaleco Feminino Acinturado",
    "Estetoscópio Littmann Classic III",
    "Fritadeira Air Fryer Mondial",
    "Robô Aspirador de Pó",
    "Garrafa Térmica Stanley",
    "Echo Dot Alexa 5ª geração",
    "Kindle 11ª geração",
    "Fire TV Stick 4K",
    "Carregador Portátil Power Bank 20000mAh"
]

def carregar_enviados(arquivo):
    if not os.path.exists(arquivo):
        return set()
    with open(arquivo, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def salvar_enviado(arquivo, item_id):
    with open(arquivo, "a", encoding="utf-8") as f:
        f.write(f"{item_id}\n")

def resetar_historico(arquivo):
    if os.path.exists(arquivo):
        try:
            os.remove(arquivo)
            print(f"Histórico reiniciado: {arquivo}")
        except Exception as e:
            print(f"Erro ao reiniciar {arquivo}: {e}")

def carregar_ofertas_ml():
    ofertas = []
    if not os.path.exists(ARQUIVO_PRODUTOS_ML):
        print(f"Aviso: {ARQUIVO_PRODUTOS_ML} não encontrado.")
        return ofertas

    with open(ARQUIVO_PRODUTOS_ML, "r", encoding="utf-8") as f:
        for linha in f:
            linha_limpa = linha.strip()
            if not linha_limpa:
                continue
            partes = [p.strip() for p in linha_limpa.split("|")]
            if len(partes) >= 2:
                ofertas.append({
                    "nome": partes[0],
                    "link": partes[1],
                    "destaque": partes[2] if len(partes) > 2 else "Oferta com Envio Rápido"
                })
    return ofertas

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
        if res.status_code == 200:
            return True
        print(f"Erro Telegram HTTP {res.status_code}: {res.text}")
        return False
    except Exception as e:
        print(f"Exceção ao contactar o Telegram: {e}")
        return False

def processar_amazon():
    enviados = carregar_enviados(HISTORICO_AMAZON)
    pendentes = [t for t in TERMOS_AMAZON if t not in enviados]

    if not pendentes:
        resetar_historico(HISTORICO_AMAZON)
        pendentes = TERMOS_AMAZON

    termo = pendentes[0]
    link = f"https://www.amazon.com.br/s?k={quote_plus(termo)}&tag={AMAZON_TAG}"
    termo_fmt = html.escape(termo)

    msg = (
        f"🔥 <b>OFERTA EM DESTAQUE NA AMAZON</b>\n\n"
        f"📦 <b>Produto:</b> {termo_fmt}\n"
        f"🚚 Entrega rápida com Amazon Prime\n"
        f"💳 Parcelamento sem juros disponível\n\n"
        f"🛒 <a href='{link}'>Aproveitar Desconto na Amazon</a>"
    )

    if enviar_telegram(msg):
        salvar_enviado(HISTORICO_AMAZON, termo)
        print(f"[AMAZON] Enviado com sucesso: {termo}")
        return True
    return False

def processar_mercado_livre():
    ofertas = carregar_ofertas_ml()
    if not ofertas:
        print("[MERCADO LIVRE] Sem produtos carregados do ficheiro txt.")
        return False

    enviados = carregar_enviados(HISTORICO_ML)
    pendentes = [item for item in ofertas if item["link"] not in enviados]

    if not pendentes:
        resetar_historico(HISTORICO_ML)
        pendentes = ofertas

    item = pendentes[0]
    nome_fmt = html.escape(item["nome"])
    destaque_fmt = html.escape(item["destaque"])
    link = item["link"]

    msg = (
        f"⚡ <b>ACHADINHO NO MERCADO LIVRE</b>\n\n"
        f"📦 <b>Produto:</b> {nome_fmt}\n"
        f"🚀 <b>Destaque:</b> {destaque_fmt}\n"
        f"🛡️ Compra 100% Garantida\n\n"
        f"👉 <a href='{link}'>Ver Oferta no Mercado Livre</a>"
    )

    if enviar_telegram(msg):
        salvar_enviado(HISTORICO_ML, link)
        print(f"[MERCADO LIVRE] Enviado com sucesso: {item['nome']}")
        return True
    return False

def executar():
    print("Iniciando ciclo Misto (Amazon + Mercado Livre)...")
    sucesso_amz = processar_amazon()
    sucesso_ml = processar_mercado_livre()
    print(f"Ciclo finalizado. Amazon: {sucesso_amz} | Mercado Livre: {sucesso_ml}")

if __name__ == "__main__":
    executar()
