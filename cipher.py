import itertools

sample_len = 10
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ,.-"
al_len = len(alphabet)

mapping = {c: i for i, c in enumerate(alphabet)}
inv_mapping = {i: c for i, c in enumerate(alphabet)}

block_len = 5

for idx_file in range(4):
    filename = f"{idx_file}.txt"
    text = open(filename).read()

    # Determine top 2 frequent letters for each substream
    top_candidates = []
    for pos in range(block_len):
        freq = {c: 0 for c in alphabet}

        for ch in text[pos::block_len]:
            if ch in freq:
                freq[ch] += 1

        ordered = sorted(freq.keys(), key=lambda c: freq[c], reverse=True)
        top_candidates.append(ordered[:2])

    print(f"text {idx_file}:")

    # Try all combinations of the top letters
    for guess in itertools.product(*top_candidates):
        # Compute shifts assuming each guessed letter maps to 'E'
        shifts = [(mapping["E"] - mapping[g]) % al_len for g in guess]
        key = "".join(inv_mapping[(al_len - s) % al_len] for s in shifts)

        # Decode text
        decoded_chars = []
        for n, ch in enumerate(text):
            if ch in mapping:
                shift = shifts[n % block_len]
                decoded_chars.append(alphabet[(mapping[ch] + shift) % al_len])
            else:
                decoded_chars.append(ch)

        print(f"Key {key}:\n{''.join(decoded_chars[:100])}")

    print()
