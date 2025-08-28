from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

# Generate an RSA keypair (for demo; normally you’d load existing keys)
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

message = b"launch codes: 0000-0000 (jk)"

# Encrypt with PUBLIC key (anyone can do this to send to the private-key holder)
ciphertext = public_key.encrypt(
    message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ),
)
print("Ciphertext (hex):", ciphertext.hex())

# Decrypt with PRIVATE key (only the holder can do this)
plaintext = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ),
)
print("Decrypted:", plaintext.decode())
