#%%
import streamlit as st
import pdfplumber
import pandas as pd
import re
from datetime import datetime
import time

#%%

# 1. Configuração da página:
st.set_page_config(page_title="GTWC Live Panel", page_icon="🏁", layout="wide", initial_sidebar_state="expanded")

# 2. Motor de extração de dados:
@st.cache_data
def extrair_dados_sro_robusto(pdf_path):
    linhas_finais = []
    dia_atual = "Data não identificada"
    dias_semana = ['WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tabela = page.extract_table()
            if not tabela: continue
            
            for row in tabela:
                celulas = [str(x).strip() if x else "" for x in row]
                texto_linha = " ".join(celulas).upper()

                for dia in dias_semana:
                    if dia in texto_linha:
                        dia_atual = texto_linha.split('\n')[0].title() 
                        break

                if celulas and re.match(r'^\d{4}', celulas[0]):
                    sessao = " ".join(celulas[3:]).replace('\n', ' ').strip()
                    if not sessao and len(celulas) > 2: sessao = celulas[2]

                    linhas_finais.append({
                        "Dia": dia_atual,
                        "Inicio": celulas[0],
                        "Fim": celulas[1] if len(celulas) > 1 else "",
                        "Sessao": sessao
                    })
    return pd.DataFrame(linhas_finais)

# 3. Função Construtora de Cards (Refatoração para código limpo):
def gerar_card_html(row, agora_dt, dia_hoje_nome, modo_grande=False):
    import re
    
    # Horário de início:
    ini_int = int(row['Inicio'])
    h_i = int(str(ini_int).zfill(4)[:2])
    m_i = int(str(ini_int).zfill(4)[2:])
    
    # Descobrindo o horário de fim:
    fim_str = str(row['Fim']).strip()
    if fim_str and fim_str != "None" and fim_str.isdigit():
        fim_int = int(fim_str)
        h_f = int(str(fim_int).zfill(4)[:2])
        m_f = int(str(fim_int).zfill(4)[2:])
    else:
        # Se não tem fim, tenta achar a duração escondida no texto (Ex: "00:45"):
        texto_sessao = str(row['Sessao']).strip()
        match_duracao = re.search(r'^(\d{2}):(\d{2})', texto_sessao)
        
        if match_duracao:
            dur_h = int(match_duracao.group(1))
            dur_m = int(match_duracao.group(2))
        else:
            dur_h = 1 # Fallback de segurança (1 hora)
            dur_m = 0
            
        # Calcula a hora de fim real somando a duração:
        m_f = m_i + dur_m
        h_f = h_i + dur_h + (m_f // 60)
        m_f = m_f % 60
        fim_int = int(f"{h_f:02d}{m_f:02d}")

    hora_atual_int = int(agora_dt.strftime("%H%M"))
    status_css = ""
    html_barra = ""
    
    # Lógica de sessão ativa e barra de progresso:
    if dia_hoje_nome in row['Dia'].upper():
        if hora_atual_int > fim_int: 
            status_css = "sessao-passada"
        elif ini_int <= hora_atual_int <= fim_int: 
            status_css = "card-ativa"
            try:
                total_mins = (h_f * 60 + m_f) - (h_i * 60 + m_i)
                if total_mins > 0:
                    passou_mins = (agora_dt.hour * 60 + agora_dt.minute) - (h_i * 60 + m_i)
                    pct = max(0, min(100, int((passou_mins / total_mins) * 100)))
                    html_barra = f"<div style='background-color: #444; border-radius: 4px; height: 6px; margin-top: 10px; overflow: hidden;'><div style='background-color: #ffaa00; width: {pct}%; height: 100%; transition: width 0.5s;'></div></div><div style='text-align: right; font-size: 0.75em; color: #ffaa00; margin-top: 2px;'>{pct}% Concluído</div>"
            except:
                pass

    # Cores e ícones:
    s_l = row['Sessao'].lower()
    c_cor, icon = "card-admin", "🗓️"
    if "practice" in s_l or "warm up" in s_l: c_cor, icon = "card-practice", "🔵"
    elif "qualifying" in s_l: c_cor, icon = "card-qualifying", "🟣"
    elif "race" in s_l: c_cor, icon = "card-race", "🟢"

    # Retorna o HTML
    if not modo_grande:
        return f"""
        <div class="sessao-card {c_cor} {status_css}" style="min-height: 80px; padding: 8px;">
            <div style="font-size: 0.9em; font-weight: bold; color: #ffaa00;">{row['Inicio']} - {fim_int:04d}</div>
            <div style="font-size: 0.8em; color: #fff; margin-top: 4px;">{row['Sessao']}</div>{html_barra}
        </div>"""
    else:
        return f"""
        <div class="sessao-card {c_cor} {status_css}">
            <div style="font-size: 1.1em; font-weight: bold; color: #ffaa00;">{row['Inicio']} - {fim_int:04d}</div>
            <div style="font-size: 0.95em; color: #ffffff; margin: 5px 0;">{icon} {row['Sessao']}</div>{html_barra}
        </div>"""

# 4. CSS:
st.markdown("""
<style>
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255, 68, 68, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(255, 68, 68, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 68, 68, 0); } }
    .card-ativa { border: 2px solid #ff4444 !important; animation: pulse 2s infinite; background-color: #2d1010 !important; }
    .sessao-passada { opacity: 0.3; filter: grayscale(80%); }
    .sessao-card { background-color: #1e1e1e; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 6px solid #555; }
    .card-practice { border-left-color: #2196F3 !important; } .card-qualifying { border-left-color: #9C27B0 !important; } .card-race { border-left-color: #4CAF50 !important; } .card-admin { border-left-color: #ff9800 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; } .stTabs [data-baseweb="tab"] { background-color: #1e1e1e; border-radius: 5px 5px 0px 0px; padding: 8px 16px; color: #fff; } .stTabs [aria-selected="true"] { background-color: #ff4444 !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 5. Interface Visual Cabeçalho:
col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.markdown("<h1 style='margin-bottom: 0;'>🏁 GTWC Australia - Painel de Box</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888; margin-top: 0;'>Cronograma Automático do Final de Semana</p>", unsafe_allow_html=True)
with col_t2:
    
    # ---------------------------------------------------------
    # TESTE ATIVO (Para ver a tela do "Carro na Pista")
    # ---------------------------------------------------------
    
    agora_dt = datetime.now()
    # Para usar o relógio real depois:

    st.markdown(f"""
        <div style="background-color: #262626; padding: 5px 20px; border-radius: 10px; border: 1px solid #444; text-align: center; margin-top: 10px;">
            <span style="color: #888; font-size: 0.8em; display: block; text-transform: uppercase;">Hora Local</span>
            <span style="color: #ffaa00; font-size: 2.2em; font-weight: bold; font-family: monospace;">{agora_dt.strftime('%H:%M')}</span>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# 6. Processamento Principal:
try:
    df = extrair_dados_sro_robusto(r"C:\Users\joaoc\OneDrive\Documentos\Arquivo_PDFs\Team Timetable_GTWC Australia_R1_Phillip Island V1 19MAR2026.pdf")

    if not df.empty:
        hora_atual_int = int(agora_dt.strftime("%H%M"))
        dia_hoje_nome = agora_dt.strftime('%A').upper() 
        df_hoje = df[df['Dia'].str.upper().str.contains(dia_hoje_nome, na=False)]

        # Radar de sessões críticas (race mode):
        sessao_critica_ativa = None
        sessao_alerta_previo = None
        agora_mins = agora_dt.hour * 60 + agora_dt.minute

        if not df_hoje.empty:
            for _, row in df_hoje.iterrows():
                s_l = str(row['Sessao']).lower()
                
                # Procura apenas pelas sessões que importam (Treinos, Quali, Corrida):
                if "practice" in s_l or "qualifying" in s_l or "race" in s_l or "warm up" in s_l:
                    # Calcula o tempo real em minutos
                    ini_int = int(row['Inicio'])
                    h_i, m_i = int(str(ini_int).zfill(4)[:2]), int(str(ini_int).zfill(4)[2:])
                    ini_mins = h_i * 60 + m_i

                    fim_str = str(row['Fim']).strip()
                    if fim_str and fim_str != "None" and fim_str.isdigit():
                        h_f, m_f = int(fim_str.zfill(4)[:2]), int(fim_str.zfill(4)[2:])
                    else:
                        import re
                        match_d = re.search(r'^(\d{2}):(\d{2})', str(row['Sessao']))
                        dur_h, dur_m = (int(match_d.group(1)), int(match_d.group(2))) if match_d else (1, 0)
                        m_f = m_i + dur_m
                        h_f = h_i + dur_h + (m_f // 60)
                        m_f = m_f % 60
                    fim_mins = h_f * 60 + m_f

                    # 1. Está acontecendo AGORA:
                    if ini_mins <= agora_mins <= fim_mins:
                        pct = int(((agora_mins - ini_mins) / (fim_mins - ini_mins)) * 100) if fim_mins > ini_mins else 0
                        sessao_critica_ativa = {
                            'Sessao': row['Sessao'],
                            'Inicio': row['Inicio'],
                            'Fim': f"{h_f:02d}{m_f:02d}",
                            'pct': max(0, min(100, pct))
                        }
                        break # Se achou, para de procurar
                    
                    # 2. Vai começar em 15 minutos ou menos:
                    elif 0 < (ini_mins - agora_mins) <= 15:
                        sessao_alerta_previo = {
                            'Sessao': row['Sessao'],
                            'Faltam': ini_mins - agora_mins
                        }

            # Faixa azul padrão (só mostra se não estiver no meio de uma corrida):
            if not sessao_critica_ativa:
                df_futuro = df_hoje[df_hoje['Inicio'].astype(int) > hora_atual_int].sort_values(by='Inicio')
                if not df_futuro.empty:
                    next_s = df_futuro.iloc[0]
                    st.info(f"🚀 **PRÓXIMA ENTRADA HOJE:** {next_s['Sessao']} às **{next_s['Inicio']}**")
                else:
                    st.success("🏁 **Fim das atividades de pista por hoje!** Retornaremos amanhã.")
        else:
            st.info("📅 Nenhuma atividade programada para a pista no dia de hoje.")

        # CAIXA DE RENDERIZAÇÃO SEGURA (ANTI-FANTASMA):
        tela_principal = st.empty()

        with tela_principal.container():
            # SEQUESTRO DE TELA (O MODO CORRIDA)
            if sessao_critica_ativa:
                html_sequestro = f"<div style='background-color: #4a0000; padding: 60px; border-radius: 20px; text-align: center; border: 4px solid #ff4444; animation: pulse 2s infinite; margin-top: 30px;'><h1 style='color: white; font-size: 5em; margin-bottom: 0; text-transform: uppercase;'>🏎️ CARRO NA PISTA</h1><h2 style='color: #ffaa00; font-size: 3em; margin-top: 10px;'>{sessao_critica_ativa['Sessao']}</h2><h3 style='color: white; font-size: 2.5em;'>{sessao_critica_ativa['Inicio']} - {sessao_critica_ativa['Fim']}</h3><div style='background-color: #222; border-radius: 15px; height: 40px; margin-top: 50px; overflow: hidden; border: 2px solid #555;'><div style='background-color: #00e676; width: {sessao_critica_ativa['pct']}%; height: 100%; transition: width 1s;'></div></div><p style='color: white; font-size: 2em; margin-top: 15px; font-weight: bold;'>{sessao_critica_ativa['pct']}% Concluído</p></div>"
                st.markdown(html_sequestro, unsafe_allow_html=True)
                
            # MODO NORMAL (CRONOGRAMA)
            else:
                # Se faltam 15 minutos, mostra um alerta vermelho gigante no topo:
                if sessao_alerta_previo:
                    st.markdown(f"""
                    <div style="background-color: #ff4444; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px;">
                        <h2 style="color: white; margin: 0;">🚨 ATENÇÃO: Pit Lane abrindo em breve!</h2>
                        <h4 style="color: white; margin: 5px 0 0 0;">A sessão <b>{sessao_alerta_previo['Sessao']}</b> começa em <b>{sessao_alerta_previo['Faltam']} minutos</b>!</h4>
                    </div>
                    """, unsafe_allow_html=True)

                dias_encontrados = list(df['Dia'].unique())
                abas = st.tabs(["📅 Visão Geral"] + dias_encontrados)

                # Aba: Visão Geral 
                with abas[0]:
                    cols = st.columns(len(dias_encontrados))
                    for i, dia in enumerate(dias_encontrados):
                        with cols[i]:
                            st.markdown(f"<h3 style='text-align:center; color:#ff4444; border-bottom: 1px solid #333;'>{dia.split()[0]}</h3>", unsafe_allow_html=True)
                            for _, row in df[df['Dia'] == dia].iterrows():
                                st.markdown(gerar_card_html(row, agora_dt, dia_hoje_nome, modo_grande=False), unsafe_allow_html=True)

                # Abas Individuais 
                for idx, dia in enumerate(dias_encontrados):
                    with abas[idx + 1]:
                        c1, c2, c3 = st.columns(3)
                        for i, row in df[df['Dia'] == dia].reset_index().iterrows():
                            with [c1, c2, c3][i % 3]:
                                st.markdown(gerar_card_html(row, agora_dt, dia_hoje_nome, modo_grande=True), unsafe_allow_html=True)

except Exception as e:
    st.error(f"⚠️ Erro ao carregar os dados: {e}")

# 7. Auto-Refresh (Para TV de Box)
time.sleep(60)
st.rerun()