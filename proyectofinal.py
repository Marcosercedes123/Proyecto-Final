import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta
from sklearn.neighbors import NearestNeighbors  # Importar NearestNeighbors de scikit-learn

# Conectar a la base de datos SQLite
conn = sqlite3.connect('ventas_belleza.db')
cursor = conn.cursor()

# Insertar datos aleatorios en la tabla productos
productos = [
    ('Shampoo', 'Cuidado del Cabello', 5.99),
    ('Acondicionador', 'Cuidado del Cabello', 6.99),
    ('Jabón', 'Cuidado de la Piel', 2.99),
    ('Crema Facial', 'Cuidado de la Piel', 12.99),
    ('Perfume', 'Fragancias', 25.99),
    ('Esmalte de Uñas', 'Cosméticos', 3.99),
    ('Lápiz Labial', 'Cosméticos', 8.99),
    ('Base de Maquillaje', 'Cosméticos', 14.99),
    ('Gel para el Cabello', 'Cuidado del Cabello', 4.99),
    ('Loción Corporal', 'Cuidado de la Piel', 9.99)
]

cursor.executemany('INSERT INTO productos (nombre, categoria, precio) VALUES (?, ?, ?)', productos)
conn.commit()

# Insertar datos aleatorios en la tabla compras
clientes = [1, 2, 3, 4, 5]
productos_ids = [i for i in range(1, 11)]
fecha_inicial = datetime.strptime('2023-01-01', '%Y-%m-%d')

compras = []

for cliente in clientes:
    for _ in range(random.randint(1, 5)):  # Cada cliente hace entre 1 y 5 compras
        producto_id = random.choice(productos_ids)
        fecha = fecha_inicial + timedelta(days=random.randint(0, 365))
        compras.append((cliente, producto_id, fecha.strftime('%Y-%m-%d')))

cursor.executemany('INSERT INTO compras (cliente_id, producto_id, fecha) VALUES (?, ?, ?)', compras)
conn.commit()

# Función para recomendar productos basados en historial de compras
def recomendar_productos(cliente_id):
    # Obtener historial de compras del cliente
    query = '''
        SELECT p.nombre, p.categoria, p.precio
        FROM compras c
        JOIN productos p ON c.producto_id = p.id
        WHERE c.cliente_id = ?
    '''
    compras_cliente = pd.read_sql_query(query, conn, params=(cliente_id,))
    
    # Si el cliente no tiene compras, no se puede recomendar nada
    if compras_cliente.empty:
        return "No se han encontrado recomendaciones para este cliente."

    # Usar Nearest Neighbors para recomendaciones
    model = NearestNeighbors(n_neighbors=5, algorithm='brute')
    productos = pd.read_sql_query('SELECT * FROM productos', conn)
    model.fit(productos[['precio']])
    
    # Recomendaciones basadas en precios similares
    _, indices = model.kneighbors(compras_cliente[['precio']])
    recomendaciones = productos.iloc[indices[0]]
    return recomendaciones[['nombre', 'categoria', 'precio']]

# Ejemplo de uso
cliente_id = 1
recomendaciones = recomendar_productos(cliente_id)
print(f"""----------------------------RECOMENDACIONES-----------------------------------
  ----------------------------------------------------------------------------------""")
print(recomendaciones)
