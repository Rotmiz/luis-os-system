# --- CÓDIGO V6: LUIS OS (CLOUD EDITION) ---
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Luis OS: Cloud", layout="wide", page_icon="☁️")

# --- ESTILO ---
st.markdown("""
<style>
    .hero-card {background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); padding: 20px; border-radius: 15px; color: white; border: 1px solid #4ca1af;}
    .stat-box {background-color: #262730; padding: 15px; border-radius: 10px; border-left: 5px solid #4ca1af; margin-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

# --- CONEXÃO COM BANCO DE DADOS (SHEETS) ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Função para carregar dados (Cria abas se não existirem)
def carregar_dados():
    try:
        # Tenta ler a aba 'player'. Se falhar, cria DF padrão
        player_df = conn.read(worksheet="player", ttl=0) # ttl=0 para não ter cache
        if player_df.empty: raise Exception("Vazio")
    except:
        player_df = pd.DataFrame([{
            'nome': 'Luis', 'nivel': 1, 'xp': 0, 'xp_next': 1000, 
            'gold': 0, 'combo': 0, 'data_viagem': '2027-09-01', 'saldo_viagem': 0.0
        }])
    
    try:
        fin_df = conn.read(worksheet="financas", ttl=0)
        if fin_df.empty: raise Exception("Vazio")
    except:
        fin_df = pd.DataFrame([{'data': str(datetime.now().date()), 'tipo': 'Inicial', 'valor': 0.0, 'obs': 'Setup'}])
        
    return player_df, fin_df

# Função para salvar dados
def salvar_player(df):
    conn.update(worksheet="player", data=df)
    st.toast("Salvando na nuvem...", icon="☁️")

def salvar_financas(df):
    conn.update(worksheet="financas", data=df)
    st.toast("Finanças atualizadas!", icon="💰")

# --- CARREGA DADOS INICIAIS ---
player_db, financas_db = carregar_dados()
p = player_db.iloc[0] # Pega a primeira linha do jogador

# --- INTERFACE ---
st.markdown(f"""
<div class='hero-card'>
    <h2>🛡️ {p['nome']} (Nvl {int(p['nivel'])})</h2>
    <div style='display: flex; justify-content: space-between;'>
        <span><b>XP:</b> {int(p['xp'])} / {int(p['xp_next'])}</span>
        <span><b>Ouro:</b> {int(p['gold'])}</span>
    </div>
    <div style='background:#555; height:10px; border-radius:5px; margin-top:5px;'>
        <div style='background:#4ca1af; width:{(p['xp']/p['xp_next'])*100}%; height:100%; border-radius:5px;'></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")
tab1, tab2, tab3 = st.tabs(["⚔️ Missões & RPG", "💰 Finanças Reais", "🗺️ Sonhos (Viagem)"])

# --- ABA 1: RPG ---
with tab1:
    st.subheader("Missões Diárias")
    c1, c2, c3 = st.columns(3)
    
    if c1.button("💧 Água (1L)"):
        player_db.at[0, 'xp'] += 10
        player_db.at[0, 'gold'] += 1
        salvar_player(player_db)
        st.success("+10 XP")
        
    if c2.button("🏋️ Treino"):
        player_db.at[0, 'xp'] += 50
        player_db.at[0, 'gold'] += 5
        salvar_player(player_db)
        st.success("+50 XP")

    if c3.button("📘 Estudo (15m)"):
        player_db.at[0, 'xp'] += 20
        player_db.at[0, 'gold'] += 2
        salvar_player(player_db)
        st.success("+20 XP")

# --- ABA 2: FINANÇAS ---
with tab3:
    st.subheader("Controle Financeiro")
    
    # Input
    with st.form("add_gasto"):
        valor = st.number_input("Valor (R$)", min_value=0.0)
        tipo = st.selectbox("Tipo", ["Gasto Fixo", "Lazer", "Investimento", "Viagem"])
        obs = st.text_input("Descrição")
        if st.form_submit_button("Registrar"):
            novo_item = pd.DataFrame([{'data': str(datetime.now().date()), 'tipo': tipo, 'valor': valor, 'obs': obs}])
            financas_db = pd.concat([financas_db, novo_item], ignore_index=True)
            salvar_financas(financas_db)
            
            # Se for Viagem, atualiza saldo do player
            if tipo == "Viagem":
                player_db.at[0, 'saldo_viagem'] += valor
                player_db.at[0, 'xp'] += int(valor) # Ganha XP por investir!
                salvar_player(player_db)
                st.balloons()
            st.rerun()

    # Visualização
    if not financas_db.empty:
        st.dataframe(financas_db.tail(5), use_container_width=True)

# --- ABA 3: VIAGEM ---
with tab2:
    st.subheader("Projeto Europa 2027")
    saldo = p['saldo_viagem']
    meta = 20000.0
    perc = min(saldo/meta, 1.0)
    
    st.metric("Fundo Atual", f"R$ {saldo:.2f}", f"Meta: R$ {meta}")
    st.progress(perc)
    
    if perc < 0.1:
        st.info("O começo é difícil. Mantenha a constância!")
    elif perc > 0.5:
        st.success("Já passamos da metade!")

# Verifica Level UP
if p['xp'] >= p['xp_next']:
    player_db.at[0, 'nivel'] += 1
    player_db.at[0, 'xp'] = 0
    player_db.at[0, 'xp_next'] = p['xp_next'] * 1.2
    salvar_player(player_db)
    st.balloons()
    st.toast("LEVEL UP!", icon="🆙")
