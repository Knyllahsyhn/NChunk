import keyring

def store_credentials (kr, username,password):
    keyring.set_password(kr,"username",username)
    keyring.set_password(kr,"password",password)

def get_stored_credentials(kr):
    username = keyring.get_password(kr,"username")
    password = keyring.get_password(kr,"password")
    return username,password 
 