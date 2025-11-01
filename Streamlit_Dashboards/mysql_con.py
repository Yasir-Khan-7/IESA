import mysql.connector

# Connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        passwd="admin123",
        db="iesa_db"
    )

def custom_hash(input_string):
    hash_val=0
    prime=31  #prime number for mixing
    mod=2**32  #Limit to simulate 32-bit unsigned integer
    for char in input_string:
        hash_val = (hash_val * prime + ord(char)) % mod
    return hex(hash_val)[2:].zfill(12)  #It Convert the numerical hash value (hash_val) into a hexadecimal string and ensure it has a consistent length by zero-padding

def validate_user(username, password):
    password=custom_hash(password)
    print("Hash is:",password)
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM user_data WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()[0]
    conn.close()
    return result > 0
# Fetch data from a table - adding this function to resolve the import error
def fetch_table_data(table_name):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = f"SELECT * FROM `{table_name}`"
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows:
            return pd.DataFrame()
        columns = [desc[0] for desc in cursor.description]
        data = pd.DataFrame(rows, columns=columns)

        # Convert MW to GWh if applicable
        if "Installed Capacity (MW)" in data.columns:
            data["Installed Capacity (MW)"] = (data["Installed Capacity (MW)"] * 8760) / 1000
            data = data.rename(columns={"Installed Capacity (MW)": "Installed Capacity (GWh)"})

        # Convert all numeric columns to float for visualization
        for col in data.columns[1:]:
            data[col] = pd.to_numeric(data[col], errors="coerce")
        data.fillna(0, inplace=True)

    except Exception as e:
        print(f"Error fetching data from {table_name}: {e}")
        data = pd.DataFrame()
    finally:
        conn.close()
    
    return data