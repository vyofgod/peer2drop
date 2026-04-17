# Peer2Drop

Secure P2P file transfer with end-to-end encryption and Device ID system.

---

## Features

- **AES-256 + RSA-2048** end-to-end encryption
- **Device ID System** - IP addresses hidden from users
- **Zero configuration** - works immediately
- **Cross-platform** - Windows, Linux, macOS
- **Real-time transfers** with progress tracking
- **Minimalist interface** - pure black design

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python3 p2p_transfer.py
```

### Usage

1. Launch app - Device ID appears at top
2. Click "Copy ID" and share with peer
3. Paste peer's Device ID and click "Add Peer"
4. Select peer and click "Connect"
5. Add files and click "Upload All"

---

## How It Works

### Device ID System

Each instance generates a unique Device ID that encodes the IP address and port:

```
Device ID: MTkyLj-E2OC4x-LjUzOj-UwMDAZ
           (contains: 192.168.1.53:5000)
```

Users only share Device IDs - IP addresses remain hidden.

### Security

- **Handshake**: RSA-2048 key exchange
- **Transfer**: AES-256 symmetric encryption
- **Verification**: SHA-256 file hashing

---

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

---

## Configuration

Files stored in `~/.p2p_transfer/`:

- `shared/` - Files to share
- `downloads/` - Received files
- `peers.json` - Peer registry

Default port: 5000 (auto-increments if busy)

---

## Architecture

```
p2p_core.py          Backend (networking, crypto, files)
p2p_transfer.py      GUI application (PyQt6)
```

### Key Components

- **DeviceID** - Generate and encode Device IDs
- **CryptoManager** - AES-256 + RSA-2048 encryption
- **FileManager** - File scanning and metadata
- **P2PConnection** - Peer-to-peer connection handling
- **P2PServer** - Accept incoming connections
- **P2PClient** - Initiate outgoing connections

---

## Troubleshooting

**Peer stays offline:**
- Ensure both apps running
- Check firewall allows port 5000
- Verify same local network

**Files not sending:**
- Click "Connect" first
- Wait for "online" status
- Check files in shared folder

---

## Dependencies

```
cryptography==41.0.7
psutil==5.9.6
PyQt6==6.6.1
pyperclip==1.8.2
```

---

## License

MIT License

Copyright (c) 2025 vyofgod

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Repository

https://github.com/vyofgod/peer2drop
