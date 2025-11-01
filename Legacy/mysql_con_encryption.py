import mysql.connector

# Connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        passwd="admin123",
        db="iesa_db" #chnage db name i set to iesa for my dbfff
    )
    
def custom_hash(input_string):
    hash_val=0
    prime=31  #prime number for mixing
    mod=2**32  #Limit to simulate 32-bit unsigned integer
    for char in input_string:
        hash_val = (hash_val * prime + ord(char)) % mod
    return hex(hash_val)[2:].zfill(12)  #IT Convert the numerical hash value (hash_val) into a hexadecimal string and ensure it has a consistent length by zero-padding

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

# def validate_user(username, password):
#     # Hash the password
#     password = custom_hash(password)
#     print("Password Hash is:", password)
    
#     # Establish database connection
#     conn = get_connection()
#     cursor = conn.cursor()
    
#     # Query to fetch all user data
#     q1 = "SELECT * FROM user_data WHERE username = %s"
    
#     # Execute the query with the correct parameter format
#     cursor.execute(q1, (username,))
#     result = cursor.fetchall()
    
#     # Print all data retrieved
#     print("All Data Retrieved from Query:")
#     for row in result:
#         print(row)
    
#     # Close the connection
#     conn.close()