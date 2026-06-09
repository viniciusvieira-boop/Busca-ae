import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import re
import base64
from pathlib import Path

st.set_page_config(
    page_title="Busca aê",
    page_icon="🔍",
    layout="wide"
)

LOGO_MANDAE_B64 = "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06dC3oyhFuW/ulrrph666a7amkYppFf+nyjfycj+Lrm79feeBMko1/x6XoW3L1eVTUVQW85rrYc5HcnsJzflY7411dZ5QQCAR3YnZm8rS2UW1V11eMrfGV/eVnnyLcMcblFa77kawBnVB1JPaKluucLXzuw7de0u4mTjUU1VlmJYkvrsN9Ov9pDivTW2RSbeVbBpbAPrMf01LMM1N99VvjK/GeTK8K01OPBzfF8PVnOBza5vL1nhx8tOYcjjlHMdH/mXa7sRLtKUH+mQzaOienT1nK5NVJtdHqLFF5QqkAnZ9Z6P0ltvKp1/2Txp9FnoW4Y9SqtGXaFYK7dOYHflJK6eIJYGCOWXqNnclsyMf+oxWrblrX5h+Hr2nmNfTrID2J8T7XnBII6xChbqaXmPPXiXJZ6ddAoxzuUn8amxkYsj+Y3OQ7gkh2BPc7k2UtJ57FtQtzaCqpA1rvK85VZOnNpPTlrn/oyejO/Es3vxG/zPBY43p2Gzs6M5iZccuoyehmG9Mevfr3nqu6ghXYA9wDOYkKTXMg9BI3okb6HU6Flg7Ow6a7ziJKlJbMHYssB2LH367nIZgSQx2e/XvPIjjk+YydK7qCFZgD30ZzESG29AIiJAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREA//Z"
LOGO_NUVEM_B64  = "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"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

/* ── Header ── */
.app-header {{
    background: #1A2EC9;
    padding: 16px 28px;
    border-radius: 10px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}
.app-header-left h1 {{
    color: white;
    font-size: 20px;
    font-weight: 700;
    margin: 0 0 2px 0;
    letter-spacing: -0.01em;
}}
.app-header-left p {{
    color: rgba(255,255,255,0.65);
    font-size: 12px;
    margin: 0;
}}
.app-header-logos {{
    display: flex;
    align-items: center;
    gap: 16px;
}}
.app-header-logos img {{
    height: 28px;
    width: auto;
    object-fit: contain;
    filter: brightness(0) invert(1);
}}
.logo-divider {{
    width: 1px;
    height: 24px;
    background: rgba(255,255,255,0.25);
}}

/* ── Cards ── */
.card {{
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 16px;
}}
.card-title {{
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .08em;
    color: #9CA3AF;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.step-num {{
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: #1A2EC9;
    color: white;
    font-size: 11px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}}

/* ── Botão primário (Buscar / Buscar tabelas) ── */
div[data-testid="stButton"] > button[kind="primary"] {{
    background: #1A2EC9 !important;
    border: none !important;
    border-radius: 7px !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    transition: background 0.15s !important;
}}
div[data-testid="stButton"] > button[kind="primary"]:hover {{
    background: #1224A8 !important;
}}

/* ── Botões secundários ── */
div[data-testid="stButton"] > button:not([kind="primary"]) {{
    border-radius: 7px !important;
    border-color: #E5E7EB !important;
    color: #374151 !important;
    font-size: 13px !important;
}}
div[data-testid="stButton"] > button:not([kind="primary"]):hover {{
    border-color: #1A2EC9 !important;
    color: #1A2EC9 !important;
    background: #EEF0FF !important;
}}

/* ── Download buttons ── */
div[data-testid="stDownloadButton"] > button {{
    background: #EEF0FF !important;
    color: #1A2EC9 !important;
    border: 1px solid #B0BAEE !important;
    border-radius: 7px !important;
    font-weight: 500 !important;
}}
div[data-testid="stDownloadButton"] > button:hover {{
    background: #1A2EC9 !important;
    color: white !important;
    border-color: #1A2EC9 !important;
}}

/* ── Input ── */
div[data-testid="stTextInput"] input {{
    border-radius: 7px !important;
    border-color: #E5E7EB !important;
}}
div[data-testid="stTextInput"] input:focus {{
    border-color: #1A2EC9 !important;
    box-shadow: 0 0 0 2px rgba(26,46,201,0.15) !important;
}}

/* ── Success box ── */
div[data-testid="stAlert"][data-baseweb="notification"] {{
    border-radius: 8px !important;
}}

/* ── Divider ── */
hr {{ border-color: #F3F4F6 !important; }}

/* ── Hide Streamlit branding ── */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header[data-testid="stHeader"] {{background: transparent;}}
</style>

<div class="app-header">
  <div class="app-header-left">
    <h1>Busca aê</h1>
    <p>Compartilhador de Tabelas — Comercial &amp; Plataforma</p>
  </div>
  <div class="app-header-logos">
    <img src="data:image/png;base64,{LOGO_MANDAE_B64}" alt="Mandaê" />
    <div class="logo-divider"></div>
    <img src="data:image/png;base64,{LOGO_NUVEM_B64}" alt="Nuvemshop" />
  </div>
</div>
""", unsafe_allow_html=True)


# ── Resto da lógica original (sem alterações) ──────────────────────────────

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
    {"key": "intelipost",     "label": "Intelipost",      "sub": "Logistica"},
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

# ── Session state ──────────────────────────────────────────────────────────

if "com_sel" not in st.session_state:
    st.session_state.com_sel = None
if "plat_sel" not in st.session_state:
    st.session_state.plat_sel = {}
if "resultados_com" not in st.session_state:
    st.session_state.resultados_com = []
if "resultados_plat" not in st.session_state:
    st.session_state.resultados_plat = {}

# ── Card 1: Busca comercial ────────────────────────────────────────────────

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-title"><span class="step-num">1</span> Buscar tabela comercial</div>', unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    termo_com = st.text_input("Buscar cliente", placeholder="Ex: MERCURIO, LUA, CALISTO...", label_visibility="collapsed", key="input_com")
with col2:
    buscar_com = st.button("Buscar", type="primary", use_container_width=True)

if buscar_com and termo_com:
    with st.spinner(f'Buscando "{termo_com}" no Drive...'):
        try:
            st.session_state.resultados_com = buscar_recursivo(FOLDER_COM, termo_com)
            st.session_state.com_sel = None
        except Exception as e:
            st.error(f"Erro: {e}")

if st.session_state.resultados_com:
    st.markdown("**Selecione a tabela comercial:**")
    for f in st.session_state.resultados_com:
        is_sel = st.session_state.com_sel and st.session_state.com_sel["id"] == f["id"]
        label = f"{'✅' if is_sel else '📄'} {f['name']}"
        if st.button(label, key=f"com_{f['id']}", use_container_width=True):
            st.session_state.com_sel = f

if st.session_state.com_sel:
    col_info, col_dl = st.columns([3, 1])
    with col_info:
        st.success(f"Selecionado: {st.session_state.com_sel['name']}")
    with col_dl:
        if st.button("Baixar tabela comercial", use_container_width=True):
            with st.spinner("Baixando..."):
                dados = baixar_arquivo(st.session_state.com_sel["id"])
                st.download_button(
                    label="Clique para salvar",
                    data=dados,
                    file_name=st.session_state.com_sel["name"],
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_com"
                )

st.markdown('</div>', unsafe_allow_html=True)

# ── Card 2: Plataformas ────────────────────────────────────────────────────

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-title"><span class="step-num">2</span> Selecione as plataformas</div>', unsafe_allow_html=True)

cols = st.columns(4)
plats_selecionadas = []
for i, plat in enumerate(PLATAFORMAS):
    with cols[i % 4]:
        checked = st.checkbox(f"{plat['label']} {plat['sub']}", key=f"chip_{plat['key']}")
        if checked:
            plats_selecionadas.append(plat)

st.divider()
tipo_filtro = st.radio("Tipo de tabela", ["Todos", "Economico (E_)", "Rapido (R_)"], horizontal=True)

buscar_plat = st.button(
    "Buscar tabelas para este cliente",
    type="primary",
    use_container_width=True,
    disabled=not (st.session_state.com_sel and len(plats_selecionadas) > 0)
)

if buscar_plat:
    nome_com = st.session_state.com_sel["name"]
    cliente, numero = extrair_partes_comercial(nome_com)

    st.session_state.resultados_plat = {}
    with st.spinner("Buscando tabelas de plataforma..."):
        try:
            todos_arquivos = buscar_recursivo(FOLDER_PLAT, cliente)
            filtrados = filtrar_por_tabela_comercial(todos_arquivos, cliente, numero)

            for plat in plats_selecionadas:
                arquivos_plat = [
                    f for f in filtrados
                    if plat["key"] in f["name"].lower() or plat["label"].lower() in f["name"].lower()
                ]
                if arquivos_plat:
                    st.session_state.resultados_plat[plat["key"]] = {"plat": plat, "files": arquivos_plat}

            if not st.session_state.resultados_plat and filtrados:
                st.session_state.resultados_plat["todos"] = {
                    "plat": {"label": "Resultados", "key": "todos"},
                    "files": filtrados
                }
        except Exception as e:
            st.error(f"Erro: {e}")
    st.session_state.plat_sel = {}

if st.session_state.resultados_plat:
    st.markdown("**Selecione as tabelas de plataforma:**")
    for key, dados in st.session_state.resultados_plat.items():
        plat = dados["plat"]
        files = dados["files"]

        if tipo_filtro == "Economico (E_)":
            files = [f for f in files if get_tipo(f["name"]) == "E"]
        elif tipo_filtro == "Rapido (R_)":
            files = [f for f in files if get_tipo(f["name"]) == "R"]

        if not files:
            continue

        st.markdown(f"**{plat['label']}** - {len(files)} arquivo(s)")
        for f in files:
            tipo = get_tipo(f["name"])
            tipo_badge = "E" if tipo == "E" else "R" if tipo == "R" else ""
            key_sel = f"plat_{f['id']}"
            checked = st.checkbox(f"{tipo_badge} {f['name']}", key=key_sel)
            if checked:
                if key not in st.session_state.plat_sel:
                    st.session_state.plat_sel[key] = []
                if not any(x["id"] == f["id"] for x in st.session_state.plat_sel[key]):
                    st.session_state.plat_sel[key].append(f)
            else:
                if key in st.session_state.plat_sel:
                    st.session_state.plat_sel[key] = [x for x in st.session_state.plat_sel[key] if x["id"] != f["id"]]

st.markdown('</div>', unsafe_allow_html=True)

# ── Card 3: Downloads ──────────────────────────────────────────────────────

todos_plat = [f for files in st.session_state.plat_sel.values() for f in files]

if todos_plat:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Downloads</div>', unsafe_allow_html=True)
    st.markdown("**Tabelas de Plataforma selecionadas:**")
    for f in todos_plat:
        tipo = get_tipo(f["name"])
        label = "Economico" if tipo == "E" else "Rapido" if tipo == "R" else "Plataforma"
        try:
            dados = baixar_arquivo(f["id"])
            st.download_button(
                label=f"{label} - {f['name']}",
                data=dados,
                file_name=f["name"],
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"dl_{f['id']}"
            )
        except Exception as e:
            st.error(f"Erro ao baixar {f['name']}: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
