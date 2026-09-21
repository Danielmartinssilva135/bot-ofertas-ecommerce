import os
import html
import requests
from urllib.parse import quote_plus

# Credenciais e IDs oficiais
TELEGRAM_TOKEN = "8633628956:AAEub3LFY8SCmkgq8FSbghoaT_hmI73ixnM"
TELEGRAM_CHAT_ID = "@superofertas_brasil2026"
AMAZON_TAG = "superofer0fb9-20"
HISTORICO_FILE = "ofertas_enviadas.txt"

# Lista completa categorizada por nichos com grande procura de compra
TERMOS_BUSCA = [
    # Bolsas Térmicas e Marmitas para Almoço
    "Bolsa Térmica Marmita Almoço Trabalho",
    "Lancheira Térmica Impermeável Fitness",
    "Bolsa Térmica 2 Compartimentos Marmiteira",
    "Kit Bolsa Térmica com Potes de Vidro Herméticos",
    "Bolsa Térmica Everbags Master",
    "Marmita Elétrica Portátil Bivolt Automóvel e Tomada",
    "Pote Térmico Inox para Sopas e Refeições Quentes",

    # Artigos para Pets (Cães e Gatos)
    "Caminha para Cachorro Confortável Lavável",
    "Fonte de Água para Gatos e Cães Automática",
    "Brinquedo Interativo Mordedor Pet",
    "Tapete Higiênico para Cães",
    "Comedouro e Bebedouro Elevado Inox Pet",
    "Escova Rasqueadeira Tira Pelos Pet",
    "Arranhador para Gatos com Brinquedo",
    "Coleira Guia Peitoral com Amortecedor",
    "Ração Royal Canin Cães e Gatos",
    "Bolsa Mochila de Transporte Pet Astronauta",

    # Moda e Beleza Feminina
    "Bolsa Feminina Transversal",
    "Bolsa Feminina de Ombro Chenson",
    "Kit de Maquiagem Completo",
    "Paleta de Sombras Océane",
    "Batom Matte Maybelline",
    "Protetor Solar Facial La Roche-Posay",
    "Perfume Feminino Importado",
    "Escova Secadora Taiff",
    "Modelador de Cachos Automático",
    "Organizador de Maquiagem Acrílico",
    
    # Profissionais da Saúde
    "Jaleco Feminino Acinturado",
    "Estetoscópio Littmann Classic III",
    "Oxímetro de Pulso Digital",
    "Esfigmomanômetro com Estetoscópio",
    "Sapato Ortopédico Hospitalar Confortável",
    "Mochila para Enfermagem e Medicina",
    "Lanterna Clínica Médica",
    "Porta Jaleco e Estetoscópio",

    # Casa e Eletroportáteis
    "Fritadeira Air Fryer Mondial",
    "Robô Aspirador de Pó",
    "Cafeteira Nespresso",
    "Garrafa Térmica Stanley",
    "Organizador de Geladeira Hermético",

    # Eletrónicos e Tecnologia
    "Echo Dot Alexa 5ª geração",
    "Kindle 11ª geração",
    "Fire TV Stick 4K",
    "Smartphone Samsung Galaxy",
    "Fone de Ouvido Bluetooth JBL",
    "Smartwatch Relógio Inteligente Feminino",
    "Carregador Portátil Power Bank 20000mAh"
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

    # Reinicia o histórico quando todos os produtos forem contemplados
    if len(enviados) >= len(TERMOS_BUSCA):
        print("Todos os produtos da lista foram enviados. Reiniciando ciclo...")
        if os.path.exists(HISTORICO_FILE):
            os.remove(HISTORICO_FILE)
        enviados = set()

    for termo in TERMOS_BUSCA:
        if enviadas_agora >= 2:
            break

        if termo in enviados:
            continue

        link_afiliado = gerar_link_afiliado_amazon(termo)
        termo_formatado = html.escape(termo)

        mensagem = (
            f"🔥 <b>OFERTA EM DESTAQUE NA AMAZON</b>\n\n"
            f"📦 <b>Produto:</b> {termo_formatado}\n"
            f"🚚 Entrega rápida com Amazon Prime\n"
            f"💳 Parcelamento sem juros disponível\n\n"
            f"🛒 <a href='{link_afiliado}'>Aproveitar Desconto na Loja</a>"
        )

        if enviar_telegram(mensagem):
            salvar_enviado(termo)
            enviadas_agora += 1
            print(f"Oferta enviada com tag de afiliado: {termo}")

    print(f"Execução concluída. Total de novas postagens: {enviadas_agora}")

if __name__ == "__main__":
    executar()
