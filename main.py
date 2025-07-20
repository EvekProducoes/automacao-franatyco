import os
import requests
import google.generativeai as genai
import sys

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


# --- 2. BUSCAR TÓPICO (VERSÃO FINAL COM BUSCA DIRETA) ---
def fetch_gaming_topic():
    """Busca notícias de games no Brasil usando uma busca por palavra-chave."""
    print("Buscando notícias de games no Brasil via busca direta...")
    
    # Usando o endpoint de busca para mais relevância
    query = '"lançamento de jogo" OR "games"'
    url = f'https://gnews.io/api/v4/search?q={query}&lang=pt&country=br&max=10&apikey={GNEWS_API_KEY}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get('articles')
        if articles:
            # Pega o primeiro artigo da lista
            first_article = articles[0]
            topic = first_article.get('title')
            article_url = first_article.get('url')
            if topic and article_url:
                print(f"Tópico de games encontrado: {topic}")
                print(f"URL da notícia: {article_url}")
                return topic, article_url
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao buscar notícias de games: {e}")

    print("Nenhum tópico de games encontrado na busca de hoje.")
    return None, None

# --- 3. BUSCAR IMAGEM RELEVANTE ---
def get_image_url(query):
    if not query: return None
    print(f"Buscando imagem para '{query}' no Pexels...")
    url = f'https://api.pexels.com/v1/search?query=games&q={query}&per_page=1&orientation=landscape'
    headers = {'Authorization': PEXELS_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        photos = response.json().get('photos')
        if photos:
            image_url = photos[0]['src']['large']
            print(f"Imagem encontrada: {image_url}")
            return image_url
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao buscar imagem: {e}")
    
    print("Nenhuma imagem encontrada para o tópico. Usando imagem de contingência.")
    return "https://images.pexels.com/photos/159393/game-machine-arcade-machine-children-s-games-159393.jpeg"

# --- 4. GERAR CONTEÚDO DO POST ---
def generate_facebook_post(topic, article_url):
    if not topic: return None
    print("Gerando texto do post com a API do Gemini...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Você é um criador de conteúdo para a página de games "Franatyco".
    Sua tarefa é criar um post para o Facebook, curto e empolgante, sobre a seguinte notícia do mundo dos games: "{topic}".
    O post deve ter um tom casual e divertido, como se estivesse conversando com outros gamers. Inclua 2 ou 3 emojis relevantes 🎮🔥.
    No final do post, adicione uma chamada para ação como "Confira a matéria completa na fonte:" e então insira a URL da notícia.
    Termine com 3 hashtags relevantes como #Games, #GamingBrasil e uma terceira relacionada ao jogo ou console da notícia.

    A URL da notícia para incluir no final é: {article_url}

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
        'caption': message,
        'url': image_url,
        'access_token': FACEBOOK_ACCESS_TOKEN
    }
    
    try:
        print("Publicando no Facebook (usando o endpoint /photos)...")
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
    topic, article_url = fetch_gaming_topic()
    
    if topic and article_url:
        post_text = generate_facebook_post(topic, article_url)
        image_url = get_image_url(topic)
        
        if post_text and image_url:
            post_to_facebook(post_text, image_url)
        else:
            print("Falha na geração do post ou busca da imagem. Publicação cancelada.")
    else:
        print("Rotina encerrada pois não foi possível obter um tópico de games hoje.")
    
    print("--- ROTINA FINALIZADA ---")
