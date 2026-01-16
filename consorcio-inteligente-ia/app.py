import streamlit as st
import sqlite3
import pandas as pd
from groq import Groq

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Consórcio Inteligente IA", layout="wide", page_icon="🚗")

# 2. CONEXÃO COM A IA (GROQ)
#coloque a sua chave da api aqui
CHAVE_GROQ = "chave"
client = Groq(api_key=CHAVE_GROQ)

def conectar():
    return sqlite3.connect('consorcio.db')

# 3. BUSCA NO BANCO DE DADOS (CLIENTE)
def buscar_planos_db(busca, v_min, v_max, renda):
    conn = conectar()
    cursor = conn.cursor()
    termo = f"%{busca}%"
    query = """
        SELECT id, categoria, nome_bem, valor_credito, taxa_adm, prazo_meses, modalidade
        FROM grupos_consorcio 
        WHERE (categoria LIKE ? OR nome_bem LIKE ?)
        AND valor_credito BETWEEN ? AND ?
        AND (valor_credito / prazo_meses) <= ?
        LIMIT 3
    """
    cursor.execute(query, (termo, termo, v_min, v_max, renda * 0.4))
    res = cursor.fetchall()
    conn.close()
    return res

# 4. INTERFACE STREAMLIT
st.title("🏛️ Consultor de Consórcio Inteligente")

tab1, tab2 = st.tabs(["👤 Área do Cliente", "🏢 Painel Admin (Gestão)"])

# ---------------- ABA DO CLIENTE ----------------
with tab1:
    st.subheader("Simulação de Contemplação")
    col1, col2, col3 = st.columns(3)
    with col1:
        nome_user = st.text_input("Teu Nome", value="Carlos")
        objetivo = st.text_input("O que desejas comprar?", value="Veículo")
    with col2:
        renda_user = st.number_input("Renda Mensal (R$)", value=5000.0)
        lance_user = st.number_input("Valor de Lance (R$)", value=15000.0)
    with col3:
        v_min, v_max = st.slider("Faixa de Crédito", 0, 1000000, (30000, 300000))
        modalidade_pref = st.selectbox("Modalidade", ["Lance Livre", "Sorteio", "Lance Fixo"])

    if st.button("Simular Melhores Estratégias"):
        planos = buscar_planos_db(objetivo, v_min, v_max, renda_user)
        if not planos:
            st.warning("Nenhum plano compatível encontrado.")
        else:
            dados_ia = []
            for p in planos:
                perc_l = (lance_user / p[3]) * 100
                st.write(f"✅ **{p[2]}** | Crédito: R${p[3]:,.2f} | Lance: {perc_l:.1f}%")
                dados_ia.append({"bem": p[2], "credito": p[3], "prazo": p[5], "perc_lance": round(perc_l, 2)})

            with st.spinner("IA processando relatório..."):
                prompt = f"O cliente {nome_user} quer {objetivo}. Planos: {dados_ia}. Renda: {renda_user}. Lance: {lance_user}. Recomende a melhor opção sem usar códigos técnicos."
                resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                st.info(resp.choices[0].message.content)

# ---------------- ABA ADMIN (ADICIONAR/EXCLUIR/LISTAR) ----------------
# ---------------- ABA ADMIN (ADICIONAR/EXCLUIR/LISTAR) ----------------
with tab2:
    st.subheader("Gestão de Inventário (Big Data)")
    
    menu_admin = st.radio("Ação:", ["Listar Tudo", "Adicionar Novo", "Remover Registo"], horizontal=True)

    if menu_admin == "Listar Tudo":
        conn = conectar()
        df = pd.read_sql_query("SELECT * FROM grupos_consorcio", conn)
        conn.close()
        st.write(f"Total de registos no sistema: **{len(df)}**")
        st.dataframe(df, use_container_width=True, hide_index=True)

    elif menu_admin == "Adicionar Novo":
        with st.form("form_add"):
            st.write("### Cadastrar Novo Plano")
            c1, c2 = st.columns(2)
            cat = c1.selectbox("Categoria", ["Veículo", "Imóvel", "Moto"])
            nome_b = c2.text_input("Nome do Bem")
            
            c3, c4, c5 = st.columns(3)
            val = c3.number_input("Crédito", min_value=1000.0)
            taxa = c4.number_input("Taxa ADM (%)", value=15.0)
            pz = c5.number_input("Prazo (Meses)", min_value=1, value=60)
            mod = st.selectbox("Modalidade", ["Sorteio", "Lance Livre", "Lance Fixo"])
            
            if st.form_submit_button("💾 Salvar"):
                conn = conectar()
                conn.execute("INSERT INTO grupos_consorcio (categoria, nome_bem, valor_credito, taxa_adm, prazo_meses, modalidade) VALUES (?,?,?,?,?,?)", (cat, nome_b, val, taxa, pz, mod))
                conn.commit(); conn.close()
                st.success("Cadastrado!")

    elif menu_admin == "Remover Registo":
        st.write("### Excluir Registo")
        id_deletar = st.number_input("Digite o ID para pesquisar:", min_value=1, step=1)
        
        # BUSCA EM TEMPO REAL
        conn = conectar()
        item = conn.execute("SELECT categoria, nome_bem, valor_credito FROM grupos_consorcio WHERE id = ?", (id_deletar,)).fetchone()
        conn.close()

        if item:
            # MOSTRA O ITEM SELECIONADO ANTES DE EXCLUIR
            st.warning(f"**Item encontrado:** {item[0]} - {item[1]} (R$ {item[2]:,.2f})")
            
            confirmar = st.checkbox(f"Eu tenho certeza que desejo excluir o ID {id_deletar}")
            
            if st.button("🗑️ Confirmar Exclusão Definitiva") and confirmar:
                conn = conectar()
                conn.execute("DELETE FROM grupos_consorcio WHERE id = ?", (id_deletar,))
                conn.commit()
                conn.close()
                st.success(f"Registo {id_deletar} removido com sucesso!")
                st.rerun() # Atualiza a tela para sumir o item excluído
        else:
            st.info("Digite um ID válido para ver os detalhes do item.")
