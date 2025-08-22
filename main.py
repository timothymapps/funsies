import hashlib
import random

class HelloWorldRange:
    def __init__(self, start=0, end=99):
        self.start = start
        self.end = end

    def guess_nonce(self, target_hash):
        """Brute force search for the nonce that matches the given hash"""
        for i in range(self.start, self.end + 1):
            text = f"Hello World {i}"
            hashed = hashlib.sha256(text.encode()).hexdigest()
            if hashed == target_hash:
                return i, hashed  # Found the nonce
        return None, None  # Not found


class NonceGenerator:
    def __init__(self, start=0, end=99):
        self.start = start
        self.end = end

    def generate(self):
        """Randomly choose a nonce, return (nonce, hash)"""
        nonce = random.randint(self.start, self.end)
        text = f"Hello World {nonce}"
        hashed = hashlib.sha256(text.encode()).hexdigest()
        return nonce, hashed


# Example usage
if __name__ == "__main__":
    # Generator creates a random nonce and hash
    generator = NonceGenerator()
    nonce, target_hash = generator.generate()
    print(f"Generated Nonce: {nonce} -> {target_hash}")

    # Range tries to guess the nonce
    finder = HelloWorldRange()
    guess, guess_hash = finder.guess_nonce(target_hash)

    if guess is not None:
        print(f"Nonce found! {guess} -> {guess_hash}")
    else:
        print("Nonce not found in range.")
