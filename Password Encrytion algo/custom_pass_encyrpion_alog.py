def custom_hash(input_string):
    hash_val=0
    prime=31  #prime number for mixing
    mod=2**32  #Limit to simulate 32-bit unsigned integer
    for char in input_string:
        # print("char:",char)
        # print("Order:",ord(char))
        hash_val = (hash_val * prime + ord(char)) % mod
        # print("HASH Value upto now:",hash_val)
    return hex(hash_val)[2:].zfill(12)  #IT Convert the numerical hash value (hash_val) into a hexadecimal string and ensure it has a consistent length by zero-padding

data = "yasirkhan2024"
hashed_val = custom_hash(data)
print(f"Custom Hash: {hashed_val}")
