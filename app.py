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

st.markdown("""
<div class="header">
  <div>
    <h1>Busca ae</h1>
    <p>Compartilhador de Tabelas - Comercial &amp; Plataforma</p>
  </div>
</div>
""", unsafe_allow_html=True)

if "com_sel" not in st.session_state:
    st.session_state.com_sel = None
if "plat_sel" not in st.session_state:
    st.session_state.plat_sel = {}
if "resultados_com" not in st.session_state:
    st.session_state.resultados_com = []
if "resultados_plat" not in st.session_state:
    st.session_state.resultados_plat = {}

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
