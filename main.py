import os
import requests
import google.generativeai as genai
import sys
from urllib.parse import quote

# --- 1. CONFIGURAÇÃO E VALIDAÇÃO DAS CHAVES ---
try:
    GEMINI_API_KEY = os.environ['GEMINI_API_KEY']
    GNEWS_API_KEY = os.environ['GNEWS_API_KEY']
    PEXELS_API_KEY = os.environ['PEXELS_API_KEY']
    FACEBOOK_PAGE_ID = os.environ['FACEBOOK_PAGE_ID']
    FACEBOOK_ACCESS_TOKEN = os.environ['FACEBOOK_ACCESS_TOKEN']
except KeyError as e:
    print(f"ERRO: A chave secreta {e} não foi encontrada. Verifique as configurações do repositório.")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)


# --- 2. BUSCAR TÓPICO DE GAMES ---
def fetch_gaming_topic():
    print("Buscando manchete de Entretenimento/Games no Brasil...")
    category = "entertainment"
    url = f'https://gnews.io/api/v4/top-headlines?category={category}&lang=pt&country=br&max=1&apikey={GNEWS_API_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get('articles')
        if articles and articles[0].get('title'):
            topic = articles[0]['title']
            print(f"Tópico de entretenimento encontrado: {topic}")
            return topic
        else:
            print(f"Nenhum artigo de '{category}' encontrado hoje.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao buscar notícias de entretenimento: {e}")
        return None

# --- 3. BUSCAR IMAGEM (MODIFICADO PARA TESTE FINAL) ---
def get_image_url(query):
    # Ignora a busca no Pexels e usa uma imagem de teste 100% confiável.
    print("Usando URL de imagem fixa para o teste final.")
    return "https://i.imgur.com/gKCHyGg.png"

# --- 4. GERAR CONTEÚDO DO POST ---
def generate_facebook_post(topic):
    if not topic: return None
    print("Gerando texto do post com a API do Gemini...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Você é um criador de conteúdo para a página de games "Franatyco".
    Sua tarefa é criar um post para o Facebook, curto e empolgante, sobre a seguinte notícia do mundo dos games: "{topic}".
    O post deve ter um tom casual e divertido, como se estivesse conversando com outros gamers. Inclua 2 ou 3 emojis relevantes 🎮🔥.
    Termine com 3 hashtags relevantes como #Games, #GamingBrasil e uma terceira relacionada ao jogo ou console da notícia.
    Responda apenas com o texto do post.
    """
    try:
        response = model.generate_content(prompt)
        print("Texto gerado com sucesso.")
        return response.text
    except Exception as e:
        print(f"ERRO ao gerar conteúdo com o Gemini: {e}")
        return None

# --- 5. PUBLICAR NO FACEBOOK ---
def post_to_facebook(message, image_url):
    if not message or not image_url:
        print("Conteúdo ou imagem faltando, publicação cancelada.")
        return
    
    post_url = f'https://graph.facebook.com/{FACEBOOK_PAGE_ID}/photos'
    payload = {
        'url': image_url,
        'message': message,
        'access_token': FACEBOOK_ACCESS_TOKEN
    }
    
    try:
        print("Publicando no Facebook...")
        response = requests.post(post_url, data=payload)
        response.raise_for_status()
        print(">>> SUCESSO! Post publicado na Página do Facebook.")
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao postar no Facebook: {e}")
        if e.response:
            print(f"Detalhes do erro: {e.response.json()}")

# --- FUNÇÃO PRINCIPAL ---
if __name__ == "__main__":
    print("--- INICIANDO ROTINA DE POSTAGEM DE GAMES ---")
    topic = fetch_gaming_topic()
    
    if topic:
        post_text = generate_facebook_post(topic)
        image_url = get_image_url(topic)
        
        if post_text and image_url:
            post_to_facebook(post_text, image_url)
        else:
            print("Falha na geração do post ou busca da imagem. Publicação cancelada.")
    else:
        print("Rotina encerrada pois não foi possível obter um tópico de games hoje.")
    
    print("--- ROTINA FINALIZADA ---")
