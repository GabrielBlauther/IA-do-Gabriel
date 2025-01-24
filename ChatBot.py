import os
import validators
from dotenv import load_dotenv
from tkinter import Tk, Label, Entry, Button, Text, END, Frame
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader, YoutubeLoader

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
if api_key is None:
    raise ValueError("Erro: A chave GROQ_API_KEY não foi encontrada. Verifique o arquivo .env.")

os.environ['GROQ_API_KEY'] = api_key

# Inicializar o modelo de IA
chat = ChatGroq(model='llama-3.1-70b-versatile')


def resposta_bot(mensagens, documento):
    """
    Gera uma resposta da IA com base nas mensagens e no documento carregado.
    """
    mensagens_system = '''Você é um assistente amigável chamado IA do Gabriel Blauther. 
    Você utiliza as seguintes informações para formular as suas respostas: {informaçoes}
    '''
    mensagens_modelo = [('system', mensagens_system)]
    mensagens_modelo += mensagens
    template = ChatPromptTemplate.from_messages(mensagens_modelo)
    chain = template | chat
    return chain.invoke({'informaçoes': documento}).content


# Funções para carregar dados
def carregar_documento(tipo, entrada_url):
    try:
        if tipo == "site":
            loader = WebBaseLoader(entrada_url)
        elif tipo == "pdf":
            loader = PyPDFLoader(entrada_url)
        elif tipo == "youtube":
            loader = YoutubeLoader.from_youtube_url(entrada_url, language=['pt'])
        else:
            raise ValueError("Tipo de documento inválido!")

        lista_documentos = loader.load()
        documento = ''.join([doc.page_content for doc in lista_documentos])
        return documento

    except Exception as e:
        return f"Erro ao carregar {tipo}: {e}"


# Funções da interface gráfica
def enviar_mensagem():
    pergunta = entrada_pergunta.get("1.0", END).strip()
    if pergunta:
        mensagens.append(('user', pergunta))
        resposta = resposta_bot(mensagens, documento_carregado)
        mensagens.append(('assistant', resposta))
        texto_respostas.insert(END, f"Você: {pergunta}\nBot: {resposta}\n\n")
        entrada_pergunta.delete("1.0", END)


def carregar_e_exibir(tipo):
    url = entrada_url.get().strip()
    if not validators.url(url):
        texto_respostas.insert(END, "Erro: URL inválida. Tente novamente.\n\n")
        return

    global documento_carregado
    documento_carregado = carregar_documento(tipo, url)
    if "Erro" not in documento_carregado:
        texto_respostas.insert(END, f"Documento {tipo} carregado com sucesso!\n\n")
    else:
        texto_respostas.insert(END, f"{documento_carregado}\n\n")


# Interface gráfica
janela = Tk()
janela.title("IA do Gabriel Blauther")
janela.geometry("600x500")

mensagens = []
documento_carregado = ''

# Layout
Label(janela, text="Digite a URL do conteúdo (site, PDF ou YouTube):").pack(pady=5)
entrada_url = Entry(janela, width=60)
entrada_url.pack(pady=5)

Label(janela, text="Escolha o tipo de conteúdo para carregar:").pack(pady=5)

frame_botoes = Frame(janela)
frame_botoes.pack(pady=5)

Button(frame_botoes, text="Carregar Site", command=lambda: carregar_e_exibir("site")).pack(side="left", padx=5)
Button(frame_botoes, text="Carregar PDF", command=lambda: carregar_e_exibir("pdf")).pack(side="left", padx=5)
Button(frame_botoes, text="Carregar YouTube", command=lambda: carregar_e_exibir("youtube")).pack(side="left", padx=5)

Label(janela, text="Digite sua pergunta:").pack(pady=5)
entrada_pergunta = Text(janela, height=5, width=60)
entrada_pergunta.pack(pady=5)

Button(janela, text="Enviar", command=enviar_mensagem).pack(pady=5)

Label(janela, text="Respostas:").pack(pady=5)
texto_respostas = Text(janela, height=20, width=90)
texto_respostas.pack(pady=5)

# Iniciar janela
janela.mainloop()
