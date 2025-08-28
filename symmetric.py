import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Sender & Receiver share this key securely out of band
key = AESGCM.generate_key(bit_length=256)      # 32 bytes
aesgcm = AESGCM(key)

nonce = os.urandom(12)                         # 96-bit nonce for GCM
plaintext = b"meet at 10:30 behind the library"
aad = b"context: ops"                          # optional associated data

ciphertext = aesgcm.encrypt(nonce, plaintext, aad)
print("Ciphertext (hex):", ciphertext.hex())

# ----- later, receiver -----
decrypted = aesgcm.decrypt(nonce, ciphertext, aad)
print("Decrypted:", decrypted.decode())
