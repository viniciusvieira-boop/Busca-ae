import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import re

st.set_page_config(
    page_title="Busca aê",
    page_icon="🔍",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.header {
    background: #00A99D; padding: 14px 24px;
    display: flex; align-items: center; gap: 12px;
    border-radius: 8px; margin-bottom: 20px;
}
.header h1 { color: white; font-size: 20px; font-weight: 600; margin: 0; }
.header p  { color: rgba(255,255,255,.7); font-size: 12px; margin: 0; }
.card {
    background: white; border: 1px solid #E0E6ED;
    border-radius: 8px; padding: 16px 20px; margin-bottom: 16px;
}
.card-title {
    font-size: 10px; font-weight: 700; text-transform: uppercase;
    letter-spacing: .06em; color: #7F8C8D; margin-bottom: 12px;
}
.step-num {
    width: 20px; height: 20px; border-radius: 50%;
    background: #00A99D; color: white; font-size: 10px;
    font-weight: 700; display: inline-flex; align-items: center;
    justify-content: center; margin-right: 6px;
}
</style>
""", unsafe_allow_html=True)

FOLDER_COM  = "1yhY8JnLQcgfOq_7rKYcbZJbiCR-yoWgT"
FOLDER_PLAT = "1skvokx1uRKgdgiRh3qUbd8qfUiatKpFA"

PLATAFORMAS = [
    {"key": "amazon",         "label": "Amazon",          "sub": "Marketplace"},
    {"key": "meli",           "label": "Mercado Livre",   "sub": "Marketplace"},
    {"key": "b2w",            "label": "B2W",             "sub": "Marketplace"},
    {"key": "via_varejo",     "label": "Via Varejo",      "sub": "Marketplace"},
    {"key": "magazine_luiza", "label": "Magalu",          "sub": "Marketplace"},
    {"key": "carrefour",      "label": "Carrefour",       "sub": "Marketplace"},
    {"key": "dafiti",         "label": "Dafiti",          "sub": "Marketplace"},
    {"key": "madeira",        "label": "Madeira Madeira", "sub": "Marketplace"},
    {"key": "vtex",           "label": "VTEX",            "sub": "Plataforma"},
    {"key": "loja_integrada", "label": "Loja Integrada",  "sub": "Plataforma"},
    {"key": "linx",           "label": "Linx",            "sub": "Plataforma"},
    {"key": "jetcommerce",    "label": "JetCommerce",     "sub": "Plataforma"},
    {"key": "ezcommerce",     "label": "EZCommerce",      "sub": "Plataforma"},
    {"key": "ciashop",        "label": "CiaShop",         "sub": "Plataforma"},
    {"key": "convertize",     "label": "Convertize",      "sub": "Plataforma"},
    {"key": "intelipost",     "label": "Intelipost",      "sub": "Logística"},
]

@st.cache_resource
def get_drive_service():
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build("drive", "v3", credentials=creds)

def listar_arquivos(folder_id, nome_filtro=None):
    service = get_drive_service()
    q = f"'{folder_id}' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'"
    if nome_filtro:
        q += f" and name contains '{nome_filtro}'"
    result = service.files().list(
        q=q,
        fields="files(id,name,webViewLink)",
        pageSize=50
    ).execute()
    return result.get("files", [])

def listar_subpastas(folder_id):
    service = get_drive_service()
    q = f"'{folder_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'"
    result = service.files().list(
        q=q,
        fields="files(id,name)",
        pageSize=50
    ).execute()
    return result.get("files", [])

def buscar_recursivo(root_id, termo):
    arquivos = listar_arquivos(root_id, termo)
    subpastas = listar_subpastas(root_id)
    for sub in subpastas:
        arquivos += listar_arquivos(sub["id"], termo)
    return arquivos

def extrair_partes_comercial(nome):
    match = re.search(r'[Vv]2?_([A-Za-z0-9]+)_([A-Za-z0-9]+)_(\d+)', nome)
    if match:
        return match.group(1).lower(), match.group(3)
    partes = re.sub(r'^[Vv]2?_', '', nome).lower().split('_')
    if len(partes) >= 3:
        return partes[0], partes[2]
    return partes[0], None

def filtrar_por_tabela_comercial(arquivos, cliente, numero):
    resultado = []
    for f in arquivos:
        nome = f["name"].lower()
        if cliente not in nome:
            continue
        if numero:
            if not re.search(rf'_{numero}[_\.]', nome):
                continue
        resultado.append(f)
    return resultado

def get_tipo(nome):
    if re.search(r'_e_|_e\d', nome, re.IGNORECASE): return "E"
    if re.search(r'_r_|_r\d', nome, re.IGNORECASE): return "R"
    return None

def baixar_arquivo(file_id):
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    buffer.seek(0)
    return buffer.read()

st.markdown("""
<div class="header">
  <div
