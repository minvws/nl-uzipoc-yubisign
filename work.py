import ctypes

dll_path = r"C:\Program Files\Yubico\Yubico PIV Tool\bin\libykcs11.dll"
try:
    my_dll = ctypes.CDLL(dll_path)
    print("DLL loaded successfully!")
except OSError as e:
    print(f"Failed to load DLL: {e}")
