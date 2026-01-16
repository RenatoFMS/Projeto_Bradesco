import sqlite3
import random

def inicializar_banco():
    print("🔄 Criando banco de dados...")
    conn = sqlite3.connect('consorcio.db')
    cursor = conn.cursor()
    
    # Limpa tabela antiga para evitar erros
    cursor.execute('DROP TABLE IF EXISTS grupos_consorcio')
    
    # Cria a tabela correta
    cursor.execute('''
        CREATE TABLE grupos_consorcio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            nome_bem TEXT NOT NULL,
            valor_credito REAL NOT NULL,
            taxa_adm REAL NOT NULL,
            prazo_meses INTEGER NOT NULL,
            modalidade TEXT NOT NULL
        )
    ''')

    # Dados para geração aleatória
    modelos = {
        'Veículo': ['Fiat Mobi', 'Hyundai HB20', 'Chevrolet Onix', 'VW Polo', 'Toyota Corolla'],
        'Imóvel': ['Apartamento Centro', 'Casa Bairro Nobre', 'Terreno Comercial', 'Loteamento'],
        'Moto': ['Honda CG 160', 'Yamaha Fazer', 'Honda Biz', 'BMW G310']
    }
    modalidades = ['Sorteio', 'Lance Livre', 'Lance Fixo']
    
    dados = []
    # Gerando 2.000 registros
    for _ in range(2000):
        cat = random.choice(list(modelos.keys()))
        nome = random.choice(modelos[cat])
        
        # Define valores baseados na categoria
        if cat == 'Imóvel': min_v, max_v = 150000, 1000000
        elif cat == 'Veículo': min_v, max_v = 40000, 150000
        else: min_v, max_v = 12000, 35000

        dados.append((
            cat, 
            nome, 
            round(random.uniform(min_v, max_v), 2), 
            round(random.uniform(12, 18), 1), # Taxa ADM
            random.randint(36, 180),          # Prazo
            random.choice(modalidades)        # Modalidade
        ))

    cursor.executemany('''INSERT INTO grupos_consorcio 
                       (categoria, nome_bem, valor_credito, taxa_adm, prazo_meses, modalidade) 
                       VALUES (?, ?, ?, ?, ?, ?)''', dados)
    
    conn.commit()
    conn.close()
    print("✅ Banco de dados criado com 2.000 registros com sucesso!")

if __name__ == "__main__":
    inicializar_banco()
