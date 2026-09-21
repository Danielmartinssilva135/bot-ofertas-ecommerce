import os
import html
import random
import requests
from urllib.parse import quote_plus

# Credenciais e IDs oficiais
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8633628956:AAEub3LFY8SCmkgq8FSbghoaT_hmI73ixnM")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "@superofertas_brasil2026")
AMAZON_TAG = os.environ.get("AMAZON_TAG", "superofer0fb9-20")

HISTORICO_AMAZON = "historico_amazon.txt"
HISTORICO_ML = "historico_mercadolivre.txt"

# 1. Catálogo Amazon (Gera busca com a tag de afiliado automaticamente)
TERMOS_AMAZON = [
    # Bolsas Térmicas e Marmitas
    "Bolsa Térmica Marmita Almoço Trabalho",
    "Lancheira Térmica Impermeável Fitness",
    "Bolsa Térmica 2 Compartimentos Marmiteira",
    "Kit Bolsa Térmica com Potes de Vidro Herméticos",
    "Bolsa Térmica Everbags Master",
    "Marmita Elétrica Portátil Bivolt Automóvel e Tomada",
    "Pote Térmico Inox para Sopas e Refeições Quentes",

    # Artigos para Pets
    "Caminha para Cachorro Confortável Lavável",
    "Fonte de Água para Gatos e Cães Automática",
    "Brinquedo Interativo Mordedor Pet",
    "Tapete Higiênico para Cães",
    "Comedouro e Bebedouro Elevado Inox Pet",
    "Escova Rasqueadeira Tira Pelos Pet",
    "Arranhador para Gatos com Brinquedo",
    "Bolsa Mochila de Transporte Pet Astronauta",

    # Moda e Cuidados
    "Bolsa Feminina Transversal",
    "Bolsa Feminina de Ombro Chenson",
    "Protetor Solar Facial La Roche-Posay",
    "Escova Secadora Taiff",
    "Organizador de Maquiagem Acrílico",

    # Saúde e Casa
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

# 2. Catálogo Mercado Livre (Cadastre aqui os produtos com os links rastreáveis do seu painel)
# Você pode ir adicionando novos produtos e links gerados no gerador de links do Mercado Livre
OFERTAS_MERCADO_LIVRE = [
    {
        "nome": "Fritadeira Sem Óleo Air Fryer Mondial 4L Inox",
        "link": "https://www.mercadolivre.com.br/afiliados/hub",
        "destaque": "Envio FULL Mercado Livre (Chega Rápido)"
    },
    {
        "nome": "Robô Aspirador de Pó Inteligente Bivolt",
        "link": "https://www.mercadolivre.com.br/afiliados/hub",
        "destaque": "Frete Grátis e Garantia de Compra"
    },
    {
        "nome": "Caminha Pet Nuvem Confort Cães e Gatos Lavável",
        "link": "https://www.mercadolivre.com.br/afiliados/hub",
        "destaque": "Vendedor Líder Gold no Mercado Livre"
    },
    {
        "nome": "Mochila Bolsa Transporte Pet Panorâmica Astronauta",
        "link": "https://www.mercadolivre.com.br/afiliados/hub",
        "destaque": "Envio Imediato Mercado Livre Full"
    },
    {
        "nome": "Kit 10 Potes de Vidro Herméticos Mantimentos",
        "link": "https://www.mercadolivre.com.br/afiliados/hub",
        "destaque": "Até 12x Sem Juros no Mercado Pago"
    }
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
        os.remove(arquivo)

def gerar_link_amazon(termo_busca):
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
        print(f"Erro no envio para o Telegram: {e}")
        return False

def processar_amazon():
    enviados = carregar_enviados(HISTORICO_AMAZON)
    if len(enviados) >= len(TERMOS_AMAZON):
        resetar_historico(HISTORICO_AMAZON)
        enviados = set()

    for termo in TERMOS_AMAZON:
        if termo in enviados:
            continue

        link = gerar_link_amazon(termo)
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
            print(f"[AMAZON] Postado: {termo}")
            return True
    return False

def processar_mercado_livre():
    enviados = carregar_enviados(HISTORICO_ML)
    if len(enviados) >= len(OFERTAS_MERCADO_LIVRE):
        resetar_historico(HISTORICO_ML)
        enviados = set()

    for item in OFERTAS_MERCADO_LIVRE:
        identificador = item["nome"]
        if identificador in enviados:
            continue

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
            salvar_enviado(HISTORICO_ML, identificador)
            print(f"[MERCADO LIVRE] Postado: {identificador}")
            return True
    return False

def executar():
    print("Iniciando ciclo Misto (Amazon + Mercado Livre)...")
    postou_amazon = processar_amazon()
    postou_ml = processar_mercado_livre()
    print(f"Ciclo finalizado. Amazon: {postou_amazon} | Mercado Livre: {postou_ml}")

if __name__ == "__main__":
    executar()
