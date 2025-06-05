_token = None

def save_token(t): global _token; _token = t
def get_token(): return _token
def clear_token(): global _token; _token = None
