# CryptXT

**Advanced File and Message Encryption Tool**

Military-grade encryption with AES-256-GCM, Argon2id key derivation, and HMAC integrity verification.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/cryptxt.svg)](https://badge.fury.io/py/cryptxt)
[![npm version](https://badge.fury.io/js/cryptxt-cli.svg)](https://badge.fury.io/js/cryptxt-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/cryptxt)](https://pepy.tech/project/cryptxt)

## Features

- **AES-256-GCM**: Authenticated encryption with built-in integrity verification
- **Argon2id**: Memory-hard key derivation (resistant to GPU attacks)
- **HMAC-SHA256**: Additional integrity verification layer
- **Cross-Platform**: Linux, macOS, Windows
- **Modern UI**: Beautiful terminal interface with progress indicators

## Quick Install

**Python (pip):**
```bash
pip install cryptxt
```

**Node.js (npx - no installation):**
```bash
npx cryptxt-cli
```

Then run:

```bash
cryptxt
```

## Installation Methods

### Option 1: pip (Recommended for Python users)

Install from PyPI:
```bash
pip install cryptxt
```

Run the application:
```bash
cryptxt
```

### Option 2: npx (No installation needed)

Run directly without installing:
```bash
npx cryptxt-cli
```

### Option 3: npm (Global install)

Install globally:
```bash
npm install -g cryptxt-cli
```

Run:
```bash
cryptxt-cli
```

### Option 4: From Source

Clone and install:
```bash
git clone https://github.com/vyofgod/CryptXT.git
cd CryptXT
pip install -r requirements.txt
python3 cryptxt.py
```

## Usage

### 1. Encrypt a Message

```bash
cryptxt
```

- Select option **1** (Encrypt Message)
- Enter your message
- Enter a strong password
- Copy the encrypted Base64 output

### 2. Decrypt a Message

- Select option **2** (Decrypt Message)
- Paste the encrypted Base64 string
- Enter the password used for encryption

### 3. Encrypt a File

- Select option **3** (Encrypt File)
- Enter file path (example: `document.pdf`)
- Enter a strong password
- File will be saved as `document.pdf.cryptxt`

### 4. Decrypt a File

- Select option **4** (Decrypt File)
- Enter encrypted file path (example: `document.pdf.cryptxt`)
- Enter the password used for encryption
- Original file will be restored

## Security Specifications

### Encryption
- **Algorithm**: AES-256-GCM
- **Key Size**: 256 bits
- **Nonce**: 12 bytes (unique per encryption)
- **Auth Tag**: 16 bytes (prevents tampering)

### Key Derivation
- **Primary**: Argon2id (3 iterations, 64 MB memory, 4 threads)
- **Fallback**: PBKDF2-HMAC-SHA256 (600,000 iterations)

### Additional Security
- HMAC-SHA256 integrity verification
- 32-byte cryptographically secure salt
- Secure random generation using `secrets` module

## Password Best Practices

**Strong passwords:**
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, special characters
- Avoid personal information

**Examples:**
- Good: `MyS3cur3P@ssw0rd!2024`
- Bad: `password123`

## Important Notes

- **No password recovery** - Encryption is irreversible without the correct password
- **Backup files** before encryption
- **Test decryption** before deleting originals
- **Store passwords** securely (use a password manager)

## Testing

```bash
# Create test file
echo "Test message" > test.txt

# Encrypt
cryptxt
# Select 3, enter: test.txt, password: test123

# Decrypt
cryptxt
# Select 4, enter: test.txt.cryptxt, password: test123
```

## Links

- **PyPI**: https://pypi.org/project/cryptxt/
- **npm**: https://www.npmjs.com/package/cryptxt-cli
- **GitHub**: https://github.com/vyofgod/CryptXT
- **Issues**: https://github.com/vyofgod/CryptXT/issues
- **Documentation**: Full installation guide in [INSTALL.md](INSTALL.md)

## Contributing

Contributions welcome! Please submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Disclaimer

This software is provided "as is" without warranty. While it uses military-grade encryption, always maintain backups of important files.

---

**Protect your data with CryptXT**

*Version 1.0.1*
