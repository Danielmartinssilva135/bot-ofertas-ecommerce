import html
import requests

# Credenciais diretas para validação imediata
TELEGRAM_TOKEN = "8633628956:AAEub3LFY8SCmkgq8FSbghoaT_hml73ixnM"
TELEGRAM_CHAT_ID = "@superofertas_brasil2026"

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

def executar():
    print("Iniciando teste de envio...")
    
    mensagem = (
        "🔥 <b>TESTE OFICIAL CONCLUÍDO COM SUCESSO!</b>\n\n"
        "📦 <b>Produto:</b> Smart TV 50 Polegadas 4K UHD\n"
        "💰 <b>Preço:</b> R$ 1.899,00\n"
        "🏬 <b>Loja:</b> Amazon Brasil\n\n"
        "🛒 <a href='https://www.amazon.com.br'>Ver Oferta no Site</a>"
    )
    
    sucesso = enviar_telegram(mensagem)
    if sucesso:
        print("Mensagem enviada para o canal com sucesso!")
    else:
        print("Falha ao enviar mensagem.")

if __name__ == "__main__":
    executar()
