import os
import mimetypes
import subprocess

# টার্মিনালে কালার প্রিন্ট করার জন্য ANSI কোড
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def get_real_mime(file_path):
    try:
        output = subprocess.check_output(['file', '--mime-type', '-b', file_path])
        return output.decode('utf-8').strip()
    except Exception:
        return None

def scan_files():
    print(f"{YELLOW}Scanning files and sub-folders...{RESET}\n" + "-" * 50)
    
    mismatch_found = False
    total_scanned = 0

    for root, dirs, files in os.walk('.'):
        for filename in files:
            filepath = os.path.join(root, filename)
            total_scanned += 1
            
            # আসল MIME টাইপ বের করা
            real_mime = get_real_mime(filepath)
            # এক্সটেনশন অনুযায়ী সাধারণ MIME টাইপ অনুমান করা
            expected_mime, _ = mimetypes.guess_type(filepath)

            if real_mime and expected_mime:
                # প্রধান টাইপ চেক করা (যেমন image vs application)
                if real_mime.split('/')[0] != expected_mime.split('/')[0] or real_mime != expected_mime:
                    # টেক্সট / প্লেইন ফাইলের ক্ষেত্রে ফলস অ্যালার্ম এড়ানোর ফিল্টার
                    if "text/" in real_mime and "text/" in expected_mime:
                        continue
                    
                    mismatch_found = True
                    # লাল রঙে মিসম্যাচ প্রিন্ট করা
                    print(f"{RED}[!] Ext mismatch found: {filepath}{RESET}")
                    print(f"    - Filename Extension suggests : {expected_mime}")
                    print(f"    - Actual File Header says     : {real_mime}\n")

    print("-" * 50)
    print(f"Total files scanned: {total_scanned}")
    
    # ফলাফল চেক করে মেসেজ প্রিন্ট করা
    if not mismatch_found:
        print(f"{GREEN}All files are passed! No extension mismatch found.{RESET}")
    else:
        print(f"{RED}Scan complete. Suspicious files detected!{RESET}")

if __name__ == "__main__":
    scan_files()