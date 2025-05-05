from flask import Flask, render_template, request, redirect, url_for
import json
import os
import re # Importa o módulo de expressões regulares para busca de padrões

# --- Configuração do App Flask ---
app = Flask(__name__)
# Caminho para o arquivo onde os dados serão salvos (temporário)
DATA_FILE = os.path.join('data', 'fan_data.json')

# Garante que a pasta data existe
os.makedirs('data', exist_ok=True)

# --- Lista de Palavras-Chave de Esports (Exemplo) ---
# Expandir esta lista melhora a análise por palavras-chave.
ESPORTS_KEYWORDS = [
    "CS2", "Counter-Strike", "Valorant", "League of Legends", "LoL",
    "Dota 2", "Fortnite", "Apex Legends", "Overwatch", "Rainbow Six Siege",
    "Rocket League", "FIFA", "FC 24", "Free Fire", "PUBG", "Esports", # Adicionado "Esports"
    "FURIA", "Liquid", "MIBR", "LOUD", "paiN Gaming", "Fluxo", "Na'Vi", "FaZe",
    "Fallen", "s1mple", "coldzera", "yay", "aspas", "falleN",
    "Major", "Qualifier", "Campeonato Brasileiro", "CBLOL", "VCT", "ESL Pro League",
    "Stream", "Pro Player", "Headshot", "Clutch", "Ace", "GG", "EZ", "MD3", "MD5",
    "Patrocinador", "Torneio", "Liga", "Equipe", "Jogador", "Caster", "Analista" # Mais termos
]

# --- Funções Auxiliares para Carregar e Salvar Dados ---
def load_fan_data():
    """Carrega os dados do arquivo JSON."""
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return {} # Retorna dicionário vazio se o arquivo não existir ou estiver vazio
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Lida com o caso do arquivo estar corrompido ou vazio
        print(f"Aviso: Arquivo JSON {DATA_FILE} vazio ou corrompido. Iniciando com dados vazios.")
        return {}
    except Exception as e:
        print(f"Erro inesperado ao carregar dados de {DATA_FILE}: {e}")
        return {}


def save_fan_data(data):
    """Salva os dados no arquivo JSON."""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar dados em {DATA_FILE}: {e}")


# --- Função de Análise Simples por Palavras-Chave ---
def analyze_interests_keywords(text_input):
    """Analisa um texto buscando por palavras-chave de esports predefinidas."""
    if not text_input:
        return []

    # Converte o texto para minúsculas para comparação sem distinção de maiúsculas/minúsculas
    text_to_analyze = text_input.lower()

    found_keywords = set() # Usamos um set para armazenar palavras-chave únicas

    # Busca cada palavra-chave na string de interesse
    for keyword in ESPORTS_KEYWORDS:
        # Cria um padrão de expressão regular para encontrar a palavra-chave como uma "palavra inteira"
        # \b representa um limite de palavra. re.escape lida com caracteres especiais na keyword.
        # Ex: '\bfuria\b' encontra "furia" mas não "furiatech" dentro do texto.
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, text_to_analyze):
            found_keywords.add(keyword) # Adiciona a palavra-chave original (não minúscula)

    # Retorna a lista de palavras-chave encontradas
    return list(found_keywords)

# --- Rotas do Aplicativo Web ---

@app.route('/')
def index():
    """Renderiza o formulário de coleta de dados."""
    # Poderíamos carregar dados existentes aqui para pré-preencher o formulário,
    # mas para este exemplo básico, o formulário começa vazio.
    return render_template('index.html')

@app.route('/save', methods=['POST'])
def save_data():
    """Recebe os dados do formulário via POST, processa e salva."""
    # Obtém todos os dados enviados no formulário
    form_data = request.form.to_dict()

    # Define os campos que esperamos que contenham listas de itens (separados por vírgula)
    list_fields = ['interesses', 'times_favoritos', 'jogadores_favoritos',
                   'atividades', 'eventos', 'compras', 'links_esports']

    processed_data = {}
    for key, value in form_data.items():
        if key in list_fields:
            # Divide a string por vírgula, remove espaços em branco e filtra itens vazios
            processed_data[key] = [item.strip() for item in value.split(',') if item.strip()]
        else:
            processed_data[key] = value # Campos simples (nome, cpf, endereco, email)

    # --- Processando e Analisando Interesses e Outros Campos Textuais ---
    # Analisar interesses usando a função de palavras-chave
    interests_text = ", ".join(processed_data.get('interesses', [])) # Junta a lista em texto
    detected_keywords_from_interests = analyze_interests_keywords(interests_text)

    # Opcional: Analisar outros campos textuais (atividades, eventos, links)
    # Junte o texto de outras listas ou campos simples para análise
    all_text_for_analysis = interests_text + " " + \
                            ", ".join(processed_data.get('atividades', [])) + " " + \
                            ", ".join(processed_data.get('eventos', [])) + " " + \
                            ", ".join(processed_data.get('links_esports', [])) # Inclui links como texto por enquanto

    detected_keywords_from_all = analyze_interests_keywords(all_text_for_analysis)
    # Remove duplicatas entre os dois conjuntos de palavras-chave detectadas
    all_detected_keywords = list(set(detected_keywords_from_interests + detected_keywords_from_all))


    print("\n--- Palavras-Chave de Esports Detectadas ---")
    print(all_detected_keywords) # Imprime no console do servidor


    # --- Exemplo: Processamento Básico de Links (sem validação de conteúdo sofisticada) ---
    # A validação REAL do conteúdo do link precisaria de mais lógica (acessar URL, raspar, analisar texto raspado)
    if 'links_esports' in processed_data and processed_data['links_esports']:
        print("\n--- Links de Esports Recebidos (Validação de Conteúdo Pendente) ---")
        for link in processed_data['links_esports']:
            print(f"- Link recebido: {link}")
            # Implementação futura: Acessar o link (requests), raspar texto (beautifulsoup4),
            # e analisar o texto raspado usando analyze_interests_keywords ou NLP.


    # --- Salvamento dos Dados ---
    # Carrega os dados existentes
    all_fan_data = load_fan_data()
    # Atualiza/adiciona os dados recebidos do formulário
    all_fan_data.update(processed_data)
    # Adiciona as palavras-chave detectadas aos dados salvos
    all_fan_data['detected_esports_keywords'] = all_detected_keywords


    # Salva os dados atualizados
    save_fan_data(all_fan_data)

    # Redireciona para a página inicial ou para uma página de sucesso
    # return redirect(url_for('index'))
    return "Dados salvos com sucesso! (Verifique o arquivo data/fan_data.json e o console do terminal)" # Mensagem de confirmação

# --- Executar o Aplicativo ---
if __name__ == '__main__':
    # IMPORTANTE: debug=True NUNCA deve ser usado em um servidor de produção
    app.run(debug=True)