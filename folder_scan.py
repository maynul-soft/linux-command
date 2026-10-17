import os

# টার্মিনালে কালার প্রিন্ট করার জন্য ANSI কোড
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

# পপুলার ফাইল ফরম্যাটের Hex Magic Signatures ম্যাপিং
HEX_SIGNATURES = {
    # Images
    '.jpg': [b'\xFF\xD8\xFF'],
    '.jpeg': [b'\xFF\xD8\xFF'],
    '.png': [b'\x89PNG\r\n\x1a\n'],
    '.gif': [b'GIF87a', b'GIF89a'],
    '.bmp': [b'BM'],
    '.webp': [b'RIFF'],  # WEBP শুরু হয় RIFF দিয়ে
    '.ico': [b'\x00\x00\x01\x00'],
    '.tiff': [b'II*\x00', b'MM\x00*'],

    # Documents / PDF / Office
    '.pdf': [b'%PDF'],
    '.zip': [b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08'], # docx, xlsx, pptx এগুলো মূলত zip ক্যাটাগরির
    '.docx': [b'PK\x03\x04'],
    '.xlsx': [b'PK\x03\x04'],
    '.pptx': [b'PK\x03\x04'],
    '.doc': [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'],
    '.xls': [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'],
    '.ppt': [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'],

    # Archives
    '.rar': [b'Rar!\x1a\x07\x00', b'Rar!\x1a\x07\x01\x00'],
    '.7z': [b'7z\xBC\xAF\'\x1C'],
    '.tar': [b'ustar'],
    '.gz': [b'\x1f\x8b'],

    # Audio & Video
    '.mp3': [b'\xFF\xFB', b'\xFF\xF3', b'\xFF\xF2', b'ID3'],
    '.mp4': [b'ftyp'], # offset এ থাকে
    '.mkv': [b'\x1A\x45\xDF\xA3'],
    '.avi': [b'RIFF'],
    '.wav': [b'RIFF'],

    # Executables
    '.exe': [b'MZ'],
    '.elf': [b'\x7fELF']
}

def get_hex_header(filepath, bytes_to_read=16):
    """ফাইল থেকে প্রথম কয়েক বাইটের Hex এবং Raw signature পড়ার ফাংশন"""
    try:
        with open(filepath, 'rb') as f:
            header_bytes = f.read(bytes_to_read)
            hex_str = ' '.join(f'{b:02X}' for b in header_bytes)
            return header_bytes, hex_str
    except Exception:
        return None, None

def detect_actual_type_from_bytes(header_bytes):
    """Hex Magic Bytes দেখে আসল ফাইলের টাইপ অনুমান করা"""
    if not header_bytes:
        return "Unknown/Unreadable"

    # চেক করা যাক জানা Signature এর সাথে মেলে কিনা
    if header_bytes.startswith(b'\xFF\xD8\xFF'):
        return "JPG/JPEG Image"
    elif header_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
        return "PNG Image"
    elif header_bytes.startswith(b'%PDF'):
        return "PDF Document"
    elif header_bytes.startswith(b'PK\x03\x04'):
        return "ZIP Archive / Office OpenXML (docx, xlsx, etc)"
    elif header_bytes.startswith(b'MZ'):
        return "Windows Executable (.exe)"
    elif header_bytes.startswith(b'GIF87a') or header_bytes.startswith(b'GIF89a'):
        return "GIF Image"
    elif header_bytes.startswith(b'Rar!'):
        return "RAR Archive"
    elif header_bytes.startswith(b'7z\xBC\xAF'):
        return "7z Archive"
    elif b'ftyp' in header_bytes[:12]:
        return "MP4 Video"
    
    # প্লেইন টেক্সট ফাইল চেক (ASCII/UTF-8 Printable characters)
    try:
        header_bytes.decode('utf-8')
        return "Plain Text / Script"
    except UnicodeDecodeError:
        return "Binary Data / Unknown Format"

def scan_files():
    print(f"{YELLOW}Starting Deep Hex-Header Scan on All Files...{RESET}\n" + "=" * 75)
    
    total_scanned = 0
    mismatch_count = 0

    for root, dirs, files in os.walk('.'):
        for filename in files:
            filepath = os.path.join(root, filename)
            total_scanned += 1
            
            ext = os.path.splitext(filename)[1].lower()
            header_bytes, hex_str = get_hex_header(filepath)
            
            if header_bytes is None:
                print(f"{RED}[!] Could not read file: {filepath}{RESET}\n")
                continue

            detected_type = detect_actual_type_from_bytes(header_bytes)
            is_mismatch = False

            # ১. যদি ফাইলটি জানা কোনো এক্সটেনশন তালিকাভুক্ত থাকে
            if ext in HEX_SIGNATURES:
                valid_signatures = HEX_SIGNATURES[ext]
                # ম্যাজিক বাইট মেলে কি না পরীক্ষা
                matched = any(
                    sig in header_bytes if ext in ['.mp4', '.tar'] else header_bytes.startswith(sig) 
                    for sig in valid_signatures
                )
                if not matched:
                    is_mismatch = True

            # ২. বিশেষ কেস: .txt এক্সটেনশন কিন্তু ভেতরে JPG/PNG/PDF/EXE এর বাইনারি হেডার
            elif ext == '.txt':
                if any(detected_type.startswith(t) for t in ["JPG", "PNG", "PDF", "ZIP", "Windows Executable"]):
                    is_mismatch = True

            # আউটপুট ডিসপ্লে
            print(f"File Name     : {CYAN}{filename}{RESET}")
            print(f"File Path     : {filepath}")
            print(f"Current Ext   : {MAGENTA}{ext if ext else 'No Extension'}{RESET}")
            print(f"Hex Header    : {hex_str[:23]}...") # প্রথম ৮ বাইটের Hex ডিসপ্লে
            print(f"Detected Type : {detected_type}")

            if is_mismatch:
                mismatch_count += 1
                print(f"Status        : {RED}[!] MISMATCH DETECTED (Fake Extension / Altered File!){RESET}")
            else:
                print(f"Status        : {GREEN}[✓] PASSED (Header matches or valid file){RESET}")
            
            print("-" * 75)

    print("=" * 75)
    print(f"Total Files Scanned : {total_scanned}")
    print(f"Mismatches Found    : {mismatch_count}")
    
    if mismatch_count == 0:
        print(f"{GREEN}Scan Complete: All files are valid!{RESET}")
    else:
        print(f"{RED}Scan Complete: Suspicious/Mismatched files detected!{RESET}")

if __name__ == "__main__":
    scan_files()
