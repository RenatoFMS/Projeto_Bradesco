import sqlite3
from groq import Groq

# Configuração da IA Groq
# coloque a sua chave aqui
CHAVE_GROQ = "chave"
client = Groq(api_key=CHAVE_GROQ)

def conectar():
    return sqlite3.connect('consorcio.db')

def cadastrar_item_banco():
    print("\n--- CADASTRAR NOVO ITEM ---")
    cat = input("Categoria: ")
    nome = input("Nome do Bem: ")
    valor = float(input("Valor do Crédito: R$ "))
    taxa = float(input("Taxa de Adm (%): "))
    prazo = int(input("Prazo (meses): "))
    mod = input("Modalidade (Sorteio/Lance): ")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO grupos_consorcio 
                   (categoria, nome_bem, valor_credito, taxa_adm, prazo_meses, modalidade_contemplacao) 
                   VALUES (?, ?, ?, ?, ?, ?)''', (cat, nome, valor, taxa, prazo, mod))
    conn.commit()
    conn.close()
    print(f"✅ '{nome}' cadastrado com sucesso!")

def listar_todos_itens(limit=2000):
    print(f"\n--- LISTA DE ITENS (TOP {limit}) ---")
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, categoria, nome_bem, valor_credito, prazo_meses FROM grupos_consorcio ORDER BY id DESC LIMIT ?", (limit,))
    itens = cursor.fetchall()
    conn.close()
    
    print(f"{'ID':<5} | {'Categoria':<15} | {'Nome do Bem':<20} | {'Valor':<12} | {'Prazo'}")
    print("-" * 70)
    for i in itens:
        print(f"{i[0]:<5} | {i[1]:<15} | {i[2]:<20} | R${i[3]:>10,.2f} | {i[4]}m")

def editar_item():
    listar_todos_itens(10)
    id_item = input("\nDigite o ID do item que deseja EDITAR: ")
    novo_valor = float(input("Novo Valor de Crédito: R$ "))
    nova_taxa = float(input("Nova Taxa de Adm (%): "))
    
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE grupos_consorcio SET valor_credito = ?, taxa_adm = ? WHERE id = ?", (novo_valor, nova_taxa, id_item))
    conn.commit()
    if cursor.rowcount > 0:
        print("✅ Item atualizado com sucesso!")
    else:
        print("❌ ID não encontrado.")
    conn.close()

def excluir_item():
    listar_todos_itens(10)
    id_item = input("\nDigite o ID do item que deseja EXCLUIR: ")
    confirmar = input(f"Tem certeza que deseja apagar o ID {id_item}? (s/n): ")
    
    if confirmar.lower() == 's':
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM grupos_consorcio WHERE id = ?", (id_item,))
        conn.commit()
        print("✅ Item removido do banco de dados.")
        conn.close()

def buscar_com_filtros():
    print("\n--- SIMULAÇÃO INTELIGENTE ---")
    busca = input("O que deseja comprar? ")
    v_min = float(input("Preço Mínimo: R$ ") or 0)
    v_max = float(input("Preço Máximo: R$ ") or 9999999)
    renda = float(input("Sua Renda Mensal: R$ "))

    conn = conectar()
    cursor = conn.cursor()
    query = """
        SELECT * FROM grupos_consorcio 
        WHERE (categoria LIKE ? OR nome_bem LIKE ?)
        AND valor_credito BETWEEN ? AND ?
        AND (valor_credito / prazo_meses) <= ?
        LIMIT 3
    """
    termo = f'%{busca}%'
    cursor.execute(query, (termo, termo, v_min, v_max, renda * 0.35))
    planos = cursor.fetchall()
    conn.close()

    if not planos:
        print("❌ Nenhum plano encontrado para este perfil.")
    else:
        print(f"✅ Planos encontrados! A IA Llama 3.1 está gerando o relatório...")
        contexto = "\n".join([f"- {p[2]}: Crédito R${p[3]:,.2f}, Taxa {p[4]}%, {p[5]} meses" for p in planos])
        prompt = f"Analise estes planos para {busca}. Calcule o custo total e recomende o melhor: {contexto}"
        
        try:
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            print("\n--- ANÁLISE DA IA ---\n", res.choices[0].message.content)
        except Exception as e:
            print(f"Erro na IA: {e}")

def main():
    while True:
        print("\n" + "="*50)
        print("      SISTEMA DE GESTÃO DE CONSÓRCIO v5.0      ")
        print("="*50)
        print("1. Simular Consórcio (Cliente)")
        print("2. Cadastrar Novo Item (Banco)")
        print("3. Editar Item Existente")
        print("4. Excluir Item do Banco")
        print("5. Listar Itens (Inventário)")
        print("6. Sair")
        
        op = input("Escolha uma opção: ")
        if op == '1': buscar_com_filtros()
        elif op == '2': cadastrar_item_banco()
        elif op == '3': editar_item()
        elif op == '4': excluir_item()
        elif op == '5': listar_todos_itens()
        elif op == '6': break
        else: print("Opção inválida.")

if __name__ == "__main__":
    main()
