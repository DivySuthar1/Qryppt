import io
import base64
import qrcode
import hashlib
import json
import datetime
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend



def generate_qr_code(data):
    """Returns base64 PNG of QR code from input data."""
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    return base64.b64encode(img_io.getvalue()).decode()


def encrypt_message(message, key, expiry_time=None):
    """Encrypt message using AES and attach expiry info if available."""
    key_bytes = hashlib.sha256(key.encode()).digest()
    iv = os.urandom(16)

    data = {'message': message, 'expiry': expiry_time.isoformat()} if expiry_time else message
    to_encrypt = json.dumps(data) if isinstance(data, dict) else data

    cipher = Cipher(algorithms.AES(key_bytes), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(to_encrypt.encode()) + encryptor.finalize()

    return base64.b64encode(iv + ciphertext).decode()


def decrypt_message(encrypted_message, key):
    """Decrypt AES message and check if it's expired."""
    try:
        key_bytes = hashlib.sha256(key.encode()).digest()
        data = base64.b64decode(encrypted_message)
        iv, ciphertext = data[:16], data[16:]

        cipher = Cipher(algorithms.AES(key_bytes), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        try:
            parsed = json.loads(plaintext.decode())
            if 'expiry' in parsed:
                expiry = datetime.fromisoformat(parsed['expiry'])
                if datetime.utcnow() > expiry:
                    return "This message has expired and is no longer available."
                return parsed['message']
            return plaintext.decode()
        except json.JSONDecodeError:
            return plaintext.decode()

    except Exception as e:
        return f"Decryption failed: {str(e)}"