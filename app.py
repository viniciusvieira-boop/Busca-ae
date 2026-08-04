import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import re
import base64
import zipfile
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

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

/* ── Botão "Baixar todas (.zip)" com destaque extra ── */
div[data-testid="stDownloadButton"]:has(button[aria-describedby="dl_all_zip"]) > button,
div[data-testid="stDownloadButton"] > button#dl_all_zip {{
    background: #1A2EC9 !important;
    color: white !important;
    border: 1px solid #1A2EC9 !important;
    font-weight: 600 !important;
}}
div[data-testid="stDownloadButton"]:has(button[aria-describedby="dl_all_zip"]) > button:hover {{
    background: #1224A8 !important;
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

_thread_local = threading.local()

def get_drive_service():
    """
    Cria/reaproveita uma instância do serviço do Drive por THREAD.

    Importante: o cliente do Google (googleapiclient, que usa httplib2 por
    baixo dos panos) NÃO é thread-safe. A versão anterior usava
    @st.cache_resource, o que fazia TODAS as threads compartilharem a
    mesma instância/conexão — quando duas threads usam esse mesmo objeto
    ao mesmo tempo (como passou a acontecer após a busca paralela),
    a conexão SSL corrompe, gerando erros como
    "[SSL] record layer failure". Por isso cada thread agora mantém sua
    própria instância isolada, criada uma vez e reaproveitada só dentro
    daquela thread.
    """
    if not hasattr(_thread_local, "service"):
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        _thread_local.service = build("drive", "v3", credentials=creds, cache_discovery=False)
    return _thread_local.service

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
            pageSize=1000,
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
        pageSize=1000
    ).execute()
    return result.get("files", [])

def buscar_recursivo(root_id, termos, max_workers=8):
    """
    Busca recursiva com cache por pasta (10 min).

    Melhoria de performance: em vez de percorrer pasta por pasta
    sequencialmente (esperando cada resposta de rede antes de pedir a
    próxima), usa um único pool de threads COMPARTILHADO para toda a
    busca, com limite fixo de `max_workers` chamadas simultâneas no total
    — não por nível de recursão. Isso importa porque a versão anterior
    criava um pool novo a cada nível (8 no nível 1, até 8×8=64 no nível 2,
    etc.), o que podia disparar rate limit da API do Drive em estruturas
    de pastas mais largas/profundas — e o retry automático do Google em
    caso de rate limit é bem mais lento que buscar sequencialmente. Com um
    único pool global, o número de chamadas simultâneas nunca passa de
    max_workers, independente do tamanho da árvore de pastas.

    termos pode ser string única ou lista de termos (todos exigidos, AND).
    """
    resultado = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures_arquivos = {executor.submit(listar_arquivos_cached, root_id, termos): root_id}
        futures_subpastas = {executor.submit(listar_subpastas_cached, root_id): root_id}
        pending = set(futures_arquivos) | set(futures_subpastas)

        while pending:
            done, pending = wait(pending, return_when=FIRST_COMPLETED)
            for future in done:
                if future in futures_arquivos:
                    resultado.extend(future.result())
                    del futures_arquivos[future]
                elif future in futures_subpastas:
                    subpastas = future.result()
                    del futures_subpastas[future]
                    for sub in subpastas:
                        f_arq = executor.submit(listar_arquivos_cached, sub["id"], termos)
                        f_sub = executor.submit(listar_subpastas_cached, sub["id"])
                        futures_arquivos[f_arq] = sub["id"]
                        futures_subpastas[f_sub] = sub["id"]
                        pending.add(f_arq)
                        pending.add(f_sub)

    return resultado


def extrair_partes_comercial(nome):
    """
    Extrai as partes que identificam a tabela comercial a partir do nome do
    arquivo selecionado.

    Ex: "V2_URANO_SPC_MVB_0.xlsx" ->
        cliente      = "urano"
        tipo_partes  = ["spc", "mvb"]   <- identifica QUAL variante da tabela
        numero       = "0"

    Importante: um mesmo cliente pode ter várias tabelas comerciais
    diferentes (SPC, SCC, SCI, SPI, MGC, MVB e combinações). O número final
    (_0, _1, _2...) por si só NÃO diferencia qual delas foi selecionada —
    por isso os segmentos do meio (tipo_partes) também precisam entrar no
    filtro, ou tabelas diferentes com o mesmo número (ex: SPC_0 e SCC_0)
    acabam se misturando na busca.
    """
    base = Path(nome).stem
    base = re.sub(r'^[Vv]2?_', '', base)
    partes = [p for p in base.split('_') if p]
    if not partes:
        return "", [], None

    cliente = partes[0].lower()
    if len(partes) >= 2 and partes[-1].isdigit():
        numero = partes[-1]
        tipo_partes = partes[1:-1]
    else:
        numero = None
        tipo_partes = partes[1:]
    tipo_partes = [p.lower() for p in tipo_partes]
    return cliente, tipo_partes, numero

def filtrar_por_tabela_comercial(arquivos, cliente, tipo_partes, numero):
    """
    Segunda camada de validação (aplicada em memória), mantida mesmo após
    empurrar o filtro para a query do Drive: `name contains` no Drive é uma
    busca simples de substring, então esse regex evita falsos positivos.

    Diferente de só checar se cada segmento de tipo_partes ESTÁ PRESENTE no
    nome, aqui é extraído o conjunto EXATO de segmentos de tipo do arquivo
    (o trecho entre o nome do cliente e o número) e comparado como conjunto
    com tipo_partes. Isso evita que uma variante com segmento extra (ex:
    "spc_mvb") passe quando o usuário selecionou só "spc".
    """
    tipo_set = set(tipo_partes)
    resultado = []
    for f in arquivos:
        nome = f["name"].lower()

        m_cliente = re.search(rf'(^|_){re.escape(cliente)}_', nome)
        if not m_cliente:
            continue
        resto = nome[m_cliente.end():]

        if numero:
            m_num = re.search(rf'_{numero}(?=[_\.])', resto)
            if not m_num:
                continue
            tipo_str = resto[:m_num.start()]
        else:
            m_er = re.search(r'_[er](?=[_\.])', resto)
            tipo_str = resto[:m_er.start()] if m_er else re.sub(r'\.[a-z0-9]+$', '', resto)

        tipo_arquivo = set(p for p in tipo_str.split('_') if p)
        if tipo_arquivo != tipo_set:
            continue

        resultado.append(f)
    return resultado

def get_tipo(nome):
    if re.search(r'_e_|_e\d', nome, re.IGNORECASE): return "E"
    if re.search(r'_r_|_r\d', nome, re.IGNORECASE): return "R"
    return None

# Cache de 10 minutos: evita baixar o mesmo arquivo mais de uma vez do Drive
# quando ele aparece tanto no botão de download individual quanto no zip
# consolidado (ver Card 3, abaixo).
@st.cache_data(ttl=600, show_spinner=False)
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

# A busca de plataforma depende de extrair cliente/tipo/número do nome do
# arquivo comercial selecionado. Isso só funciona de forma confiável para
# arquivos .xlsx que seguem o padrão V2_CLIENTE_TIPO_NUMERO (ex: propostas
# em .docx não seguem esse padrão e geram termos de busca sem sentido).
com_sel_valido = (
    st.session_state.com_sel is not None
    and st.session_state.com_sel["name"].lower().endswith(".xlsx")
)

if st.session_state.com_sel and not com_sel_valido:
    st.warning(
        "A tabela comercial selecionada não é uma planilha (.xlsx), então não é "
        "possível identificar cliente/tipo/número para buscar as tabelas de "
        "plataforma. Selecione um arquivo .xlsx no passo 1."
    )

buscar_plat = st.button(
    "Buscar tabelas para este cliente",
    type="primary",
    use_container_width=True,
    disabled=not (com_sel_valido and len(plats_selecionadas) > 0)
)

if buscar_plat:
    nome_com = st.session_state.com_sel["name"]
    cliente, tipo_partes, numero = extrair_partes_comercial(nome_com)

    # Escopa a query do Drive com cliente + tipo(s) da tabela (ex: "spc",
    # "mvb") + número, em vez de trazer tudo e filtrar depois. Reduz o
    # volume retornado pela API do Drive já na origem. A busca em cada
    # subpasta acontece em paralelo (ver buscar_recursivo), o que também
    # reduz bastante o tempo total em relação a percorrer sequencialmente.
    termos_busca = [cliente] + tipo_partes
    if numero:
        termos_busca.append(f"_{numero}")

    st.session_state.resultados_plat = {}
    with st.spinner("Buscando tabelas de plataforma..."):
        try:
            todos_arquivos = buscar_recursivo(FOLDER_PLAT, termos_busca)
            # Filtro fino: exige cliente + o conjunto exato de tipo(s)
            # (ex: "spc" ou "spc"+"mvb") + número, evitando misturar
            # variantes diferentes do mesmo cliente (ex: SPC_0 x SCC_0 x
            # SPC_MVB_0). Necessário porque `name contains` no Drive é
            # substring simples e a query acima só reduz o volume, não
            # garante exatidão.
            filtrados = filtrar_por_tabela_comercial(todos_arquivos, cliente, tipo_partes, numero)

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
    # Monta a lista de arquivos visíveis considerando o filtro de tipo (Todos
    # / Economico / Rapido) atual, para o botão "selecionar todas" agir
    # exatamente sobre o que está na tela, e não sobre tudo que foi
    # encontrado na busca.
    arquivos_visiveis = []
    for key, dados in st.session_state.resultados_plat.items():
        files = dados["files"]
        if tipo_filtro == "Economico (E_)":
            files = [f for f in files if get_tipo(f["name"]) == "E"]
        elif tipo_filtro == "Rapido (R_)":
            files = [f for f in files if get_tipo(f["name"]) == "R"]
        arquivos_visiveis.extend(files)

    col_titulo, col_sel_all = st.columns([3, 1])
    with col_titulo:
        st.markdown("**Selecione as tabelas de plataforma:**")

    if arquivos_visiveis:
        chaves_checkbox = [f"plat_{f['id']}" for f in arquivos_visiveis]
        todas_marcadas = all(st.session_state.get(k, False) for k in chaves_checkbox)
        with col_sel_all:
            label_btn = "Desmarcar todas" if todas_marcadas else "Selecionar todas"
            if st.button(label_btn, use_container_width=True, key="btn_selecionar_todas"):
                # Sobrescreve o estado de cada checkbox antes do rerun. Como
                # os checkboxes usam essas mesmas chaves (key=key_sel, abaixo),
                # eles já nascem marcados/desmarcados na próxima renderização,
                # e o loop que popula plat_sel roda normalmente sobre o novo
                # estado.
                for k in chaves_checkbox:
                    st.session_state[k] = not todas_marcadas
                st.rerun()

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

    col_titulo, col_baixar_all = st.columns([3, 1])
    with col_titulo:
        st.markdown("**Tabelas de Plataforma selecionadas:**")

    with col_baixar_all:
        # Monta um .zip único com todos os arquivos selecionados. Streamlit
        # não permite disparar vários st.download_button de uma vez com um
        # único clique (e navegadores bloqueiam múltiplos downloads
        # simultâneos como se fosse pop-up spam), então o .zip é a forma
        # confiável de entregar "baixar todas" em um clique só.
        with st.spinner("Preparando .zip..."):
            zip_buffer = io.BytesIO()
            erros_zip = []
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in todos_plat:
                    try:
                        zf.writestr(f["name"], baixar_arquivo(f["id"]))
                    except Exception as e:
                        erros_zip.append((f["name"], e))
            zip_buffer.seek(0)

        st.download_button(
            label="Baixar todas (.zip)",
            data=zip_buffer,
            file_name="tabelas_plataforma.zip",
            mime="application/zip",
            use_container_width=True,
            key="dl_all_zip"
        )

    for nome_erro, erro in erros_zip if todos_plat else []:
        st.error(f"Erro ao baixar {nome_erro} para o .zip: {erro}")

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
       
        
