@part cyber-crypto | Cryptography and PKI | crypto
## Encoding, hashing and encryption are three different things

Beginners (and some code reviewers) mix these up, and the mistake becomes a vulnerability.

| | Purpose | Reversible? | Needs a key? | Examples |
|---|---|---|---|---|
| **Encoding** | change the format so data fits a medium | yes, by anyone | no | Base64, URL encoding, hex |
| **Hashing** | a fixed-size fingerprint | **no** | no (HMAC does) | SHA-256, SHA-3, bcrypt for passwords |
| **Encryption** | hide data from anyone without the key | yes, with the key | yes | AES, ChaCha20, RSA |

`YWRtaW46cGFzc3dvcmQ=` is **Base64** of `admin:password`. It hides nothing. HTTP Basic authentication is exactly this, which is why it must only travel over HTTPS. If you find passwords "protected" by Base64 in a code review, that is a finding.

## Cryptographic hash functions

A hash function maps any input to a fixed-size output. The properties that matter:

- **Deterministic:** the same input always gives the same output.
- **Pre-image resistance:** given a hash, you cannot find an input that produces it.
- **Second pre-image resistance:** given one input, you cannot find a different input with the same hash.
- **Collision resistance:** you cannot find any two inputs with the same hash.
- **Avalanche effect:** changing one bit of input changes about half the output bits.

| Algorithm | Output | Status |
|---|---|---|
| MD5 | 128 bits (32 hex characters) | **broken** for collisions. Do not use for security |
| SHA-1 | 160 bits (40 hex) | **broken** for collisions (a practical collision was shown in 2017). Being retired |
| SHA-256 | 256 bits (64 hex) | secure, the general-purpose default |
| SHA-512 | 512 bits (128 hex) | secure |
| SHA-3 | 224 to 512 bits | secure, a different design from SHA-2 |

The **birthday bound** says collisions in an n-bit hash appear after about 2^(n/2) attempts, so a 128-bit hash gives only about 64 bits of collision security.

**Uses of hashing:** file integrity (published checksums), digital signatures (sign the hash, not the whole file), Git commit IDs, deduplication and, with extra care, password storage.

### HMAC: a hash with a key

A plain hash proves nothing about who made it, because anyone can compute it. **HMAC** mixes a secret key into the hash: `HMAC(key, message)`. Only holders of the key can produce or verify the tag, which gives **integrity and authenticity**. Webhooks, API request signing and JWTs with `HS256` all use HMAC-SHA-256. Always compare tags with a **constant-time** function to avoid timing leaks.

!cheat Hash cheat codes ::
- **Lengths:** MD5 128 bits = 32 hex, SHA-1 160 = 40 hex, SHA-256 256 = 64 hex, SHA-512 512 = 128 hex.
- **Broken for collisions:** MD5 and SHA-1. Use SHA-256 or better.
- **Collision effort:** about 2^(n/2) for an n-bit hash.
- **Hash is not encryption:** you cannot "decrypt" a hash, you can only guess and compare.
- **Need to prove who sent it?** Use HMAC (shared key) or a digital signature (private key).
!end

## Symmetric encryption

One **shared secret key** both encrypts and decrypts. It is fast, so it carries the bulk of the data. The hard part is sharing the key safely.

- **AES** is the standard block cipher. Block size is always **128 bits**. Key sizes are **128, 192 or 256 bits**. DES (56-bit key) is broken and 3DES is deprecated.
- **ChaCha20-Poly1305** is a modern stream cipher with authentication, common on phones and in TLS 1.3.
- A **block cipher mode** says how to encrypt more than one block:

| Mode | Behaviour | Verdict |
|---|---|---|
| **ECB** | each block encrypted independently | **never use**: identical plaintext blocks give identical ciphertext blocks and patterns leak (the famous encrypted penguin picture) |
| **CBC** | each block is XORed with the previous ciphertext, needs a random IV | acceptable but gives **no integrity** and has padding-oracle attacks if misused |
| **CTR** | turns the cipher into a stream cipher | fast, also no integrity |
| **GCM** | CTR plus an authentication tag (**AEAD**) | **the default choice**: encrypts and detects tampering |

- An **IV or nonce** is a non-secret value that makes each encryption different. For **GCM the nonce must never repeat under the same key**, because a repeat breaks both secrecy and authenticity.
- **Encryption without authentication** allows an attacker to flip bits in the ciphertext and change the plaintext in a predictable way. Use an AEAD mode.
- **Key length vs password:** an AES key is random bytes, a password is not. To derive a key from a password use a slow function (PBKDF2, scrypt or Argon2).

```java AES-256-GCM with the Java standard library
SecureRandom random = new SecureRandom();
byte[] nonce = new byte[12];                  // 96-bit nonce, new for every message
random.nextBytes(nonce);

Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
cipher.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(128, nonce));   // 128-bit tag
byte[] ciphertext = cipher.doFinal(plaintext);  // the 16-byte tag is appended
// Store nonce + ciphertext together. Decrypting with the wrong key or a modified byte throws AEADBadTagException.
```

!warning Do not invent crypto :: Use a reviewed library (the JDK, Bouncy Castle, Google Tink) and its high-level API. Never write your own cipher, never reuse a nonce, never hard-code a key in source code, and never use `java.util.Random` for anything secret. Use `SecureRandom`.

## Asymmetric (public-key) cryptography

Each party has a **key pair**: a public key that can be shared and a private key that never leaves its owner. What one key does, only the other can undo.

| Goal | Use | How |
|---|---|---|
| **Confidentiality** | encrypt with the **recipient's public key**, they decrypt with their private key | |
| **Authenticity and non-repudiation** | **sign with your private key**, anyone verifies with your public key | digital signature |
| **Agree on a shared key** | key exchange (Diffie-Hellman, ECDH) | both sides compute the same secret without sending it |

- **RSA** relies on the difficulty of factoring a large number n = p × q. Use at least **2048-bit** keys. **ECC** (elliptic curve cryptography) gives similar strength with far shorter keys: 256-bit ECC is roughly as strong as 3072-bit RSA. **Ed25519** and **ECDSA** are common signature schemes.
- Asymmetric operations are slow, so real systems use them only to **exchange a key or sign a hash**, and then switch to symmetric encryption. This is called **hybrid encryption** and it is what TLS does.
- **Digital signature flow:** hash the message, encrypt/sign the hash with the private key, send message and signature. The receiver hashes the message and checks the signature with the public key. A changed message gives a different hash and the check fails.

### Toy RSA: do this once to understand it

Take p = 61, q = 53 (real keys use primes of 1000+ bits).

1. n = p × q = **3233**
2. φ(n) = (p − 1)(q − 1) = 60 × 52 = **3120**
3. Choose e = **17** (coprime to 3120). Public key = (3233, 17).
4. d = e⁻¹ mod φ(n) = **2753**. Private key = (3233, 2753).
5. Encrypt m = 65: c = 65¹⁷ mod 3233 = **2790**. Decrypt: 2790²⁷⁵³ mod 3233 = 65.

Textbook RSA like this is insecure without padding (OAEP for encryption, PSS for signatures). Real libraries add it for you.

### Diffie-Hellman in one example

Public values p = 23 and g = 5. Alice picks secret a = 6 and sends A = 5⁶ mod 23 = 8. Bob picks b = 15 and sends B = 5¹⁵ mod 23 = 19. Alice computes 19⁶ mod 23 = 2. Bob computes 8¹⁵ mod 23 = 2. They share the secret **2** and an eavesdropper who saw only 23, 5, 8 and 19 cannot easily get it. Unauthenticated DH is open to a man-in-the-middle, which is why certificates are needed.

!cheat Public-key cheat codes ::
- **Encrypt to someone:** their **public** key. **Sign as yourself:** your **private** key.
- **Verify a signature:** the signer's **public** key.
- **Private key leaked = start over:** revoke, reissue, rotate.
- **Sizes:** RSA ≥ 2048 bits, ECC 256 bits (≈ RSA 3072), AES 128 or 256 bits.
- **Hybrid:** asymmetric for the key exchange or signature, symmetric (AES-GCM) for the data.
!end

## TLS and the certificate system

**TLS** (Transport Layer Security) protects HTTP and many other protocols. It gives **confidentiality** (encryption), **integrity** (authentication tags) and **server authentication** (a certificate).

### How a TLS 1.3 connection starts

1. **ClientHello:** the client sends supported versions and cipher suites and its key share.
2. **ServerHello and certificate:** the server picks the options, returns its key share and its **certificate**, and proves it owns the private key.
3. Both sides derive the same session keys using (EC)DHE, then switch to symmetric encryption (AES-GCM or ChaCha20-Poly1305).

- **Forward secrecy:** because every session uses fresh ephemeral DH keys, stealing the server's private key later does not decrypt recorded old traffic. TLS 1.3 makes this mandatory.
- **Versions:** SSL 2.0, SSL 3.0, TLS 1.0 and TLS 1.1 are obsolete and should be disabled. Use **TLS 1.2 and 1.3**. TLS 1.3 removes old weak options and completes the handshake in one round trip.
- **mTLS (mutual TLS):** the server also demands a client certificate. Common between internal services.

### Certificates and certificate authorities

An **X.509 certificate** binds a public key to an identity (a domain name) and is signed by a **certificate authority (CA)**. Browsers and operating systems ship a list of trusted **root CAs**. A server usually presents a **chain**: its own certificate, signed by an intermediate CA, signed by a root.

A client accepts a certificate only if all of these hold:

- the chain leads to a **trusted root** and every signature is valid,
- the certificate is **within its validity dates** and not **revoked** (CRL or OCSP),
- the **domain name matches** the Subject Alternative Name,
- the certificate may be used for this purpose.

```bash Looking at a certificate (any site you are allowed to connect to)
openssl s_client -connect example.com:443 -servername example.com </dev/null | openssl x509 -noout -subject -issuer -dates
```

- **Let's Encrypt** issues free, automated certificates that last 90 days and renew automatically.
- **HSTS** (`Strict-Transport-Security` header) tells the browser to use HTTPS only for a domain, so an attacker cannot downgrade the connection.
- **Self-signed certificates** are fine for local development but give no third-party proof of identity. Never tell users to click through a certificate warning.
- **Certificate pinning** ties a client to a specific key or certificate. It is powerful but can break the app when keys rotate.

## Storing passwords properly

A password must never be stored in clear text or encrypted (encryption can be reversed if the key leaks). It must be stored as a **slow, salted hash**.

| Idea | Why |
|---|---|
| **Salt**: a random value (16 bytes or more) generated per user and stored with the hash | the same password gives different hashes, so precomputed **rainbow tables** are useless and one cracked hash does not reveal others |
| **Pepper**: a secret value kept outside the database (an HSM or secret store) | a stolen database alone is not enough to crack hashes |
| **Slow, memory-hard hashing** | a plain SHA-256 can be computed billions of times a second on a GPU. A deliberately slow function cuts that to thousands |

Use one of: **Argon2id** (first choice in OWASP's Password Storage Cheat Sheet), **scrypt**, **bcrypt** (cost factor 10 or more) or **PBKDF2** (a very high iteration count). Check the cheat sheet for current parameters because hardware keeps improving. Spring Security's `DelegatingPasswordEncoder` stores the algorithm in the hash (`{bcrypt}$2a$10$...`), so you can upgrade algorithms later.

```java Spring Security password hashing
PasswordEncoder encoder = new BCryptPasswordEncoder(12);   // cost factor 12 = 2^12 rounds
String hash = encoder.encode(rawPassword);                 // the salt is generated and stored inside the hash
boolean ok = encoder.matches(rawPassword, hash);           // constant-time comparison
```

### How strong is a password?

Entropy in bits = length × log₂(size of the alphabet), for a randomly chosen password.

| Password | Alphabet | Entropy |
|---|---|---|
| 8 random lowercase letters | 26 | 8 × 4.70 = **37.6 bits** |
| 8 random from letters and digits (62) | 62 | 8 × 5.95 = **47.6 bits** |
| 12 random from 94 printable characters | 94 | 12 × 6.55 = **78.7 bits** |
| 6 random Diceware words | 7776 | 6 × 12.9 = **77.5 bits** |

**Length beats complexity.** "Password1!" looks complex but is on every cracking list. A long random passphrase or a password manager beats a short symbol-filled word. Check passwords against lists of breached passwords, and do not force periodic changes without a reason (NIST SP 800-63B recommends against it).

!cheat Password storage cheat codes ::
- **Never** plain text, Base64, reversible encryption, or a fast hash such as MD5 or one round of SHA-256.
- **Always** a unique random **salt** per password and a **slow** algorithm: Argon2id, scrypt, bcrypt or PBKDF2.
- **Pepper** lives outside the database.
- **Entropy** = length × log₂(alphabet). Each extra random character is worth 5 to 6.5 bits.
- **Rainbow tables** are defeated by salts. **GPU cracking** is slowed by work factors.
- Reset passwords by a one-time, expiring link. Never e-mail the old password (you should not be able to).
!end

!interview "What happens when you type https://bank.com?" :: DNS resolves the name. The client opens a TCP connection and sends a ClientHello. The server returns a certificate chain and a key share. The client validates the chain (trusted root, dates, name, revocation), both sides derive session keys with ephemeral Diffie-Hellman, and everything afterwards is encrypted and authenticated with AES-GCM or ChaCha20-Poly1305. HSTS stops downgrade to HTTP.

!keypoints Encoding is not encryption and hashing is not reversible ;; Use SHA-256 or better, never MD5 or SHA-1 for security ;; Use authenticated encryption such as AES-GCM and never reuse a nonce ;; Encrypt to the public key, sign with the private key ;; TLS 1.3 uses ephemeral key exchange for forward secrecy ;; Store passwords with a salt and a slow algorithm such as Argon2id or bcrypt

?? Why is Base64 not a way to protect a password?
=> Base64 is an encoding with no key. Anyone can decode it instantly.
?? How many hex characters does a SHA-256 digest have, and why is MD5 unsuitable for signatures?
=> 64 hex characters (256 bits). MD5 is broken for collisions, so an attacker can create two different documents with the same hash.
?? What is the problem with AES in ECB mode?
=> Identical plaintext blocks produce identical ciphertext blocks, so patterns in the data remain visible. Use GCM or another authenticated mode.
?? Alice wants to send Bob a secret that only Bob can read, and Bob wants to know it came from Alice. Which keys are involved?
=> Alice encrypts with Bob's public key (so only Bob can decrypt) and signs with her own private key (so Bob can verify with Alice's public key).
?? Compute the toy RSA ciphertext of m = 65 with n = 3233 and e = 17, and say what the private exponent is.
=> c = 65^17 mod 3233 = 2790. The private exponent is d = 2753.
?? Why do we salt passwords?
=> The salt makes identical passwords produce different hashes, so precomputed rainbow tables fail and cracking one hash gives no clue about another.
