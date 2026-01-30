import itertools

sample_len = 10
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ,.-"
al_len = len(alphabet)
mapping = { c:n for n,c in enumerate(alphabet) }
inv_mapping = { n:c for n,c in enumerate(alphabet) }

block_len = 5

for i in [1,2,3,4]:
    filename = f"{i}.txt"
    text = open(filename).read()
    
    # For each substream, get top 2 frequent letters
    top_letters_per_substream = []
    for j in range(block_len):
        count = { c:0 for c in alphabet }
        for c in text[j::block_len]:
            count[c] += 1
        
        # sort letters by frequency descending
        sorted_letters = sorted(count, key=lambda x: count[x], reverse=True)
        top_letters_per_substream.append(sorted_letters[:2])
    
    print(f"text {i}: ")

    # Generate all combinations of top letters (2^block_len)
    for candidate_letters in itertools.product(*top_letters_per_substream):
        # Compute shifts assuming candidate letters correspond to 'E'
        shifts = [(mapping["E"] - mapping[c]) % al_len for c in candidate_letters]
        key = "".join([inv_mapping[(al_len-s) % al_len] for s in shifts])
        
        # Decode first 60 chars
        decoded = []
        for idx, char in enumerate(text[:]):
            if char in mapping:
                shift = shifts[idx % block_len]
                decoded.append(alphabet[(mapping[char] + shift) % al_len])
            else:
                decoded.append(char)
        
        print(f"Key {key}:\n" + "".join(decoded[:100]))
    
    print()
