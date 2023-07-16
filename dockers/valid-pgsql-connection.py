import psycopg2

# connect to pgSQL with CLI : 
  # psql -h localhost -p 5432 -U admin -d postgres

# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    user="admin",
    password="password",
    database="public_data"
)

# Verify the connection
cursor = conn.cursor()
cursor.execute("SELECT * FROM ev_population LIMIT 5;")
print(cursor.fetchall())

# Close the connection
cursor.close()
conn.close()