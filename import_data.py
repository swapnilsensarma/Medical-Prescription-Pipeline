import csv
import mysql.connector

print("Connecting to database...")

# 1. Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin",  # <--- PUT YOUR MYSQL PASSWORD HERE
    database="medicines"
)
cursor = conn.cursor()

print("Building the table from scratch...")

# 2. Kill any ghost tables and build a fresh, perfect table
cursor.execute("DROP TABLE IF EXISTS medicines")
cursor.execute("""
    CREATE TABLE medicines (
        id INT,
        name TEXT,
        substitute0 TEXT,
        substitute1 TEXT,
        substitute2 TEXT,
        price INT
    )
""")

print("Reading CSV and force-feeding MySQL... (This will take about 10-20 seconds)")

# 3. Open the file and inject the data
with open('pharmacy_database_final.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)  # Skip the header row

    sql = "INSERT INTO medicines (id, name, substitute0, substitute1, substitute2, price) VALUES (%s, %s, %s, %s, %s, %s)"

    batch = []
    rows_inserted = 0

    for row in reader:
        try:
            # Grab id, name, sub0, sub1, sub2, and price (last column)
            data = (row[0], row[1], row[2], row[3], row[4], row[-1])
            batch.append(data)
        except IndexError:
            continue

        # Insert 10,000 rows at a time
        if len(batch) >= 10000:
            cursor.executemany(sql, batch)
            conn.commit()
            rows_inserted += len(batch)
            print(f"Inserted {rows_inserted} rows...")
            batch = []

    # Insert any leftover rows
    if batch:
        cursor.executemany(sql, batch)
        conn.commit()
        rows_inserted += len(batch)

print(f"SUCCESS! {rows_inserted} rows successfully forced into the database.")

cursor.close()
conn.close()
