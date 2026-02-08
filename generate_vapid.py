from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64

# Generate private key
private_key = ec.generate_private_key(ec.SECP256R1())

# Serialize private key
private_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Generate public key
public_key = private_key.public_key()
public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)

def urlsafe_b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

print("VAPID PUBLIC KEY:")
print(urlsafe_b64(public_bytes))

print("\nVAPID PRIVATE KEY:")
print(urlsafe_b64(private_bytes))
