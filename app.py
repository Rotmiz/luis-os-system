import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Luis OS: Master RPG", layout="wide", page_icon="⚔️")

# --- ESTILO CSS (GAMIFICAÇÃO VISUAL) ---
st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    .boss-card {
        background: linear-gradient(180deg, #2b1055 0%, #000000 100%);
        border: 2px solid #9c88ff;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 20px rgba(156, 136, 255, 0.3);
    }
    .boss-img {
        border-radius: 10px;
        border: 3px solid #e84118;
        margin-bottom: 10px;
    }
    .quest-btn {
        width: 100%;
        border: 1px solid #44bd32;
        color: white;
    }
    .stat-box {
        background-color: #1e272e;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #00d2d3;
        margin-bottom: 5px;
    }
    h1, h2, h3 {font-family: 'Helvetica', sans-serif;}
</style>
""", unsafe_allow_html=True)

# --- CONEXÃO ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÕES DE CARREGAMENTO (IGUAIS AO ANTERIOR) ---
def carregar_dados():
    try:
        player_df = conn.read(worksheet="player", ttl=0)
        if player_df.empty: raise Exception
    except:
        # Cria padrão se falhar (com colunas novas de atributos)
        player_df = pd.DataFrame([{
            'nome': 'Luis', 'nivel': 1, 'xp': 0, 'xp_next': 1000, 
            'gold': 0, 'str': 1, 'int': 1, 'fin': 1, # Novos Atributos
            'boss_ebook': 0, 'boss_viagem': 0
        }])
    return player_df

def salvar_player(df):
    conn.update(worksheet="player", data=df)
    st.toast("Progresso Salvo!", icon="💾")

player_db = carregar_dados()
p = player_db.iloc[0]

# --- FUNÇÕES VISUAIS ---
def render_radar_chart(str_stat, int_stat, fin_stat):
    categories = ['FORÇA (Saúde)', 'INTELIGÊNCIA (Estudo)', 'FINANÇAS (Ouro)', 'CARISMA (Social)', 'AGILIDADE (Produtividade)']
    # Simulando os outros 2 status baseados na média para fechar o pentágono
    avg = (str_stat + int_stat + fin_stat) / 3
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[str_stat, int_stat, fin_stat, avg, avg],
        theta=categories,
        fill='toself',
        name='Stats',
        line_color='#00d2d3'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 20])), # Max stat 20
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=40, b=40)
    )
    return fig

# --- INTERFACE ---

# 1. CABEÇALHO DO PASSE DE BATALHA
st.markdown(f"### 🛡️ Passe de Batalha: Temporada 1")
xp_perc = min(p['xp'] / p['xp_next'], 1.0)
st.progress(xp_perc)
c1, c2 = st.columns([1, 6])
with c1: st.image("https://api.dicebear.com/7.x/avataaars/svg?seed=LuisHero", width=80)
with c2: 
    st.write(f"**Nível {int(p['nivel'])}** | XP: {int(p['xp'])} / {int(p['xp_next'])} | 💰 Ouro: {int(p['gold'])}")
    st.caption("Próxima Recompensa: Skin 'Engenheiro Sênior' (Nvl 5)")

st.divider()

col_rpg, col_boss = st.columns([1, 2])

# --- COLUNA ESQUERDA: ATRIBUTOS & MISSÕES ---
with col_rpg:
    st.subheader("📊 Atributos")
    # Garante que as colunas existem (caso sua planilha seja antiga)
    if 'str' not in player_db.columns: player_db['str'] = 1
    if 'int' not in player_db.columns: player_db['int'] = 1
    if 'fin' not in player_db.columns: player_db['fin'] = 1
    
    # Renderiza o Gráfico Radar
    fig = render_radar_chart(p['str'], p['int'], p['fin'])
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📜 Daily Quests")
    
    if st.button("🏋️ Treino Pesado (+FOR)"):
        player_db.at[0, 'xp'] += 50
        player_db.at[0, 'str'] += 0.1 # Upa atributo
        salvar_player(player_db)
        st.rerun()
        
    if st.button("📚 Estudo Python/BIM (+INT)"):
        player_db.at[0, 'xp'] += 30
        player_db.at[0, 'int'] += 0.1
        salvar_player(player_db)
        st.rerun()

    if st.button("💰 Economizou Dia (+FIN)"):
        player_db.at[0, 'xp'] += 20
        player_db.at[0, 'fin'] += 0.1
        salvar_player(player_db)
        st.rerun()

# --- COLUNA DIREITA: CHEFÕES VISUAIS ---
with col_boss:
    st.subheader("⚔️ Chefões da Temporada")
    
    # BOSS 1: O EBOOK (Lich King do Conhecimento)
    # Lógica Visual: Imagem muda conforme o progresso
    progresso_ebook = p.get('boss_ebook', 0) # 0 a 100
    
    img_boss = "https://i.pinimg.com/originals/e8/ba/25/e8ba252917952f23aa4f72f8837e192a.gif" # Boss Vivo
    status_boss = "Vivo e Ameaçador"
    
    if progresso_ebook >= 100:
        img_boss = "https://media1.giphy.com/media/l41lUjUgLLwWvz3apO/giphy.gif" # Tesouro
        status_boss = "DERROTADO"
    elif progresso_ebook > 50:
        img_boss = "https://i.gifer.com/7S8u.gif" # Boss Machucado/Enfraquecido
        status_boss = "Enfurecido (50% HP)"

    st.markdown(f"""
    <div class='boss-card'>
        <h3>🧟 Boss: O Ebook Infinito</h3>
        <img src='{img_boss}' width='100%' style='border-radius:10px; border:2px solid red;'>
        <p>Status: <b>{status_boss}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Controle de Dano (Progresso)
    novo_progresso = st.slider("Causar Dano (Progresso %)", 0, 100, int(progresso_ebook))
    if novo_progresso != int(progresso_ebook):
        player_db.at[0, 'boss_ebook'] = novo_progresso
        if novo_progresso == 100 and progresso_ebook < 100:
            st.balloons()
            player_db.at[0, 'xp'] += 1000 # Bônus enorme por matar boss
        salvar_player(player_db)
        st.rerun()

    st.write("---")
    
    # BOSS 2: A VIAGEM (O Dragão de Ouro)
    st.write("### 🐉 Boss: Eurotrip 2027")
    progresso_viagem = p.get('boss_viagem', 0)
    
    # Barra de Vida do Boss (Estilo Jogo de Luta)
    cor_barra = "green" if progresso_viagem > 50 else "red"
    st.markdown(f"**HP do Boss (R$ Necessário)**")
    st.progress(progresso_viagem/100)
    
    aporte = st.number_input("Ataque Crítico (Aporte R$)", value=0.0, step=100.0)
    if st.button("Atacar Dragão (Investir)"):
        # Lógica simplificada: R$ 20.000 = 100%
        dano_percentual = (aporte / 20000.0) * 100
        player_db.at[0, 'boss_viagem'] = min(progresso_viagem + dano_percentual, 100)
        player_db.at[0, 'fin'] += 0.2
        salvar_player(player_db)
        st.success(f"Você causou {dano_percentual:.1f}% de dano!")
        st.rerun()

# Level UP Check
if p['xp'] >= p['xp_next']:
    player_db.at[0, 'nivel'] += 1
    player_db.at[0, 'xp'] = 0
    player_db.at[0, 'xp_next'] = p['xp_next'] * 1.5
    salvar_player(player_db)
    st.balloons()
