import hashlib
password = 'Farzam'
salt = "jzx"
dataBase_password = password+salt
hashed = hashlib.md5(dataBase_password.encode())
print(hashed.hexdigest())