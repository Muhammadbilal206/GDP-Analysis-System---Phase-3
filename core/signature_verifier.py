import hashlib

class SignatureVerifier:
    def __init__(self, secret_key, iterations):
        self.secret_key = secret_key
        self.iterations = iterations

    def verify(self, raw_value, signature):
        val_str = f"{raw_value:.2f}"
        hash_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            self.secret_key.encode('utf-8'),
            val_str.encode('utf-8'),
            self.iterations
        )
        return hash_bytes.hex() == signature
