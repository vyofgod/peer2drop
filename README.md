# Peer2Drop

**Secure P2P File Transfer with End-to-End Encryption**

Military-grade encryption with AES-256-GCM, RSA-2048 key exchange, and Device ID system.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/peer2drop.svg)](https://badge.fury.io/py/peer2drop)
[![npm version](https://badge.fury.io/js/peer2drop.svg)](https://badge.fury.io/js/peer2drop)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **AES-256 + RSA-2048**: End-to-end encryption with authenticated key exchange
- **Device ID System**: IP addresses hidden from users - share only Device IDs
- **Zero Configuration**: Works immediately, auto-detects local IP
- **Cross-Platform**: Linux, macOS, Windows
- **Real-time Transfers**: Progress tracking with speed and ETA
- **Minimalist Interface**: Pure black terminal/GUI design

## Quick Install

**Python (pip):**
```bash
pip install peer2drop
```

**Node.js (npx - no installation):**
```bash
npx peer2drop
```

Then run:

```bash
peer2drop
```

## Installation Methods

### Option 1: pip (Recommended for Python users)

Install from PyPI:
```bash
pip install peer2drop
```

Run the application:
```bash
peer2drop
```

### Option 2: npx (No installation needed)

Run directly without installing:
```bash
npx peer2drop
```

### Option 3: npm (Global install)

Install globally:
```bash
npm install -g peer2drop
```

Run:
```bash
peer2drop
```

### Option 4: From Source

Clone and install:
```bash
git clone https://github.com/vyofgod/peer2drop.git
cd peer2drop
pip install -r requirements.txt
python3 p2p_transfer.py
```

## Usage

### 1. Start the Application

```bash
peer2drop
```

Your Device ID will appear at the top:
```
Device ID: MTkyLj-E2OC4x-LjUzOj-UwMDAZ  |  Port: 5000
```

### 2. Share Your Device ID

Click **"Copy ID"** button and share with your peer.

### 3. Add a Peer

- Paste your peer's Device ID in the input field
- Click **"Add Peer"**

### 4. Connect

- Select the peer from the list
- Click **"Connect"**
- Wait for "online" status

### 5. Transfer Files

- Go to **Files** tab
- Click **"Add File (Browse)"** or **"Scan Folder"**
- Go to **Transfers** tab
- Click **"Upload All"**

## Security Specifications

### Encryption
- **Algorithm**: AES-256-GCM (Fernet)
- **Key Exchange**: RSA-2048 with OAEP padding
- **Handshake**: Secure symmetric key exchange

### Device ID System
Each instance generates a unique Device ID that encodes the IP address and port:

```
Device ID: MTkyLj-E2OC4x-LjUzOj-UwMDAZ
           (contains: 192.168.1.53:5000)
```

Users only share Device IDs - IP addresses remain hidden.

### Additional Security
- SHA-256 file hashing for verification
- Cryptographically secure random generation
- Per-session key generation

## Interface

```
Device ID: MTkyLj-E2OC4x-LjUzOj-UwMDAZ  |  Port: 5000

[Files]  [Peers]  [Transfers]

Name              Size        Hash
document.pdf      2.3 MB      9d5f6c4a
photo.jpg         1.1 MB      3e8a2b7f

[Add File]  [Scan Folder]  [Open Folder]

Server:5000 | Peers:2 | Files:5 (12.3MB) | AES-256
```

## Configuration

Files stored in `~/.p2p_transfer/`:

- `shared/` - Files to share
- `downloads/` - Received files
- `peers.json` - Peer registry

Default port: 5000 (auto-increments if busy)

## Troubleshooting

**Peer stays offline:**
- Ensure both apps are running
- Check firewall allows port 5000
- Verify same local network

**Files not sending:**
- Click "Connect" first
- Wait for "online" status
- Check files in shared folder

**Port already in use:**
- App auto-increments to next available port
- Check Device ID for actual port number

## Links

- **PyPI**: https://pypi.org/project/peer2drop/
- **npm**: https://www.npmjs.com/package/peer2drop
- **GitHub**: https://github.com/vyofgod/peer2drop
- **Issues**: https://github.com/vyofgod/peer2drop/issues

## Dependencies

```
cryptography>=41.0.0
psutil>=5.9.0
PyQt6>=6.6.0
pyperclip>=1.8.0
```

## Contributing

Contributions welcome! Please submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Disclaimer

This software is provided "as is" without warranty. While it uses military-grade encryption, always maintain backups of important files.

---

**Secure file transfers with Peer2Drop**

*Version 1.0.0*
