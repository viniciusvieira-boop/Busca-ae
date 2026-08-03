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

LOGO_MANDAE_B64 = "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"
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


# ── Configuração das pastas ────────────────────────────────────────────────

# ✅ FOLDER_COM atualizado para o novo Drive
FOLDER_COM  = "1I_G69usGZBSkJCIbJtNbYw_h10Qct703"
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

@st.cache_data(ttl=600, show_spinner=False)
def listar_arquivos_cached(folder_id, nomes_filtro=None):
    """
    Lista arquivos de uma pasta. Cache de 10 minutos.

    nomes_filtro pode ser:
      - None: sem filtro de nome
      - string: um único termo (`name contains 'termo'`)
      - lista de strings: todos os termos precisam aparecer no nome (AND),
        o que permite escopar a query já no Drive (ex: cliente + número
        da tabela comercial) em vez de trazer tudo e filtrar depois em Python.
    """
    service = get_drive_service()
    q = f"'{folder_id}' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'"
    if nomes_filtro:
        termos = [nomes_filtro] if isinstance(nomes_filtro, str) else nomes_filtro
        for termo in termos:
            q += f" and name contains '{termo}'"
    arquivos = []
    page_token = None
    while True:
        result = service.files().list(
            q=q,
            fields="nextPageToken, files(id,name,webViewLink)",
            pageSize=100,
            pageToken=page_token
        ).execute()
        arquivos += result.get("files", [])
        page_token = result.get("nextPageToken")
        if not page_token:
            break
    return arquivos

@st.cache_data(ttl=600, show_spinner=False)
def listar_subpastas_cached(folder_id):
    """Lista subpastas de uma pasta. Cache de 10 minutos."""
    service = get_drive_service()
    q = f"'{folder_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'"
    result = service.files().list(
        q=q,
        fields="files(id,name)",
        pageSize=100
    ).execute()
    return result.get("files", [])

def buscar_recursivo(root_id, termos):
    """
    Busca sequencial recursiva com cache por pasta.
    Na primeira busca percorre tudo; nas seguintes usa cache (10 min).

    termos pode ser string única ou lista de termos (todos exigidos, AND).
    """
    arquivos = listar_arquivos_cached(root_id, termos)
    subpastas = listar_subpastas_cached(root_id)
    for sub in subpastas:
        arquivos += buscar_recursivo(sub["id"], termos)
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
    """
    Segunda camada de validação (aplicada em memória), mantida mesmo após
    empurrar o filtro para a query do Drive: `name contains` no Drive é uma
    busca simples de substring, então esse regex evita falsos positivos
    (ex: número aparecendo em outra parte do nome que não seja o sufixo
    da tabela comercial).
    """
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

    # ── Melhoria: escopar a query do Drive com cliente + número da tabela
    # comercial selecionada (em vez de buscar só por "cliente" e filtrar
    # tudo depois em Python). Isso reduz o volume de arquivos retornado
    # pela API do Drive já na origem, deixando a busca mais rápida.
    termos_busca = [cliente, f"_{numero}"] if numero else [cliente]

    st.session_state.resultados_plat = {}
    with st.spinner("Buscando tabelas de plataforma..."):
        try:
            todos_arquivos = buscar_recursivo(FOLDER_PLAT, termos_busca)
            # Mantida como segunda camada de validação: `name contains` no
            # Drive é substring simples, então o regex aqui evita falsos
            # positivos que a query ampla possa trazer.
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
