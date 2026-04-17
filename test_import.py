#!/usr/bin/env python3
"""Quick import test"""
try:
    from p2p_core import *
    print("✓ Core imported successfully")
    print(f"✓ DeviceID: {DeviceID.generate()}")
    print(f"✓ MessageType count: {len(MessageType)}")
    print("✓ All imports working!")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
