import hashlib
def generate_hash(title, company):
    hash_input = f"{title}{company}".encode('utf-8')
    return hashlib.sha256(hash_input).hexdigest()