import hashlib

def validate_hash(metric, expected_hash, secret, rounds):
    formatted_val = f"{metric:.2f}"
    derived_key = hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=secret.encode("utf-8"),
        salt=formatted_val.encode("utf-8"),
        iterations=rounds
    ).hex()
    return derived_key == expected_hash

def calc_moving_mean(data_window):
    if not data_window:
        return 0.0
    return sum(data_window) / len(data_window)
