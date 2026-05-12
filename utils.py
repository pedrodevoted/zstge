import os
import shutil
import subprocess
import display
import png_handler
import jpeg_handler
import pdf_handler


def run_exiftool(args: list[str]) -> str | None:
    """Run ExifTool and return stdout, or None on failure / not found."""
    exiftool_path = shutil.which("exiftool")
    if not exiftool_path:
        print(
            f"{display.red}[!] ExifTool not found in PATH.\n"
            f"{display.yellow}    Install: apt install exiftool  |  "
            f"brew install exiftool  |  cpan Image::ExifTool"
        )
        return None
    try:
        result = subprocess.run(
            [exiftool_path] + args,
            capture_output=True,
            encoding='latin-1', errors='replace'
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"{display.red}[!] Error running ExifTool: {e}")
        return None


def scan_image_metadata(file_path: str) -> None:
    if not os.path.isfile(file_path):
        print(f"\n{display.red}[!] Invalid file path: {file_path}")
        return

    print(f"\nScanning: {file_path}")

    output = run_exiftool([file_path])
    if output:
        lines = output.splitlines()
        filtered = "\n".join(
            line for line in lines
            if "ExifTool Version Number" not in line
        )
        print(f"\n{display.yellow}ExifTool metadata:\n{display.white}{filtered}")
    else:
        print(f"{display.red}[!] Unable to scan metadata or ExifTool not available.")

    if file_path.lower().endswith(".png"):
        text_chunks = png_handler.list_text_chunks(file_path)
        if text_chunks:
            print(f"\n{display.yellow}PNG tEXt chunks (raw):{display.white}")
            for keyword, text in text_chunks:
                marker = f" {display.byellow}[zstge]{display.white}" \
                    if keyword == "zstge" else ""
                print(f"  {keyword}: {text}{marker}")

def hide_message(file_path: str, message: str) -> bool:
    ext = _ext(file_path)

    if ext == ".png":
        return png_handler.insert_message(file_path, message)

    if ext in (".jpg", ".jpeg"):
        return jpeg_handler.insert_message(file_path, message)

    if ext == ".webp":
        if shutil.which("exiftool"):
            import subprocess
            r = subprocess.run(
                ["exiftool", "-Comment", "-b", file_path],
                capture_output=True, encoding='latin-1', errors='replace'
            )
            original_comment = r.stdout.strip()
            r2 = subprocess.run(
                ["exiftool", "-UserComment", "-b", file_path],
                capture_output=True, encoding='latin-1', errors='replace'
            )
            if r2.stdout.startswith("zstge\x00"):
                print(f"\n{display.red}[!] A zstge message is already embedded. Remove it first.")
                return False
            sentinel = f"zstge\x00{original_comment}"
            result = subprocess.run(
                ["exiftool", f"-Comment={message}", f"-UserComment={sentinel}",
                 "-overwrite_original", file_path],
                capture_output=True, encoding='latin-1', errors='replace'
            )
            if result.returncode == 0:
                return True
            print(f"\n{display.red}[!] ExifTool WEBP insert failed: {result.stdout}")
            return False
        print(f"\n{display.red}[!] ExifTool required for non-destructive WEBP metadata insertion.")
        return False

    if ext == ".pdf":
        return pdf_handler.insert_message(file_path, message)

    print(f"\n{display.red}[!] Unsupported format for message hiding: {ext or '(no extension)'}")
    return False

def remove_metadata(file_path: str) -> bool:
    ext = _ext(file_path)

    if ext == ".png":
        return png_handler.remove_message(file_path)

    if ext in (".jpg", ".jpeg"):
        return jpeg_handler.remove_message(file_path)

    if ext == ".webp":
        if shutil.which("exiftool"):
            import subprocess
            r = subprocess.run(
                ["exiftool", "-UserComment", "-b", file_path],
                capture_output=True, encoding='latin-1', errors='replace'
            )
            comment_val = r.stdout
            if not comment_val.startswith("zstge\x00"):
                return True 
            original = comment_val[len("zstge\x00"):]
            args = ["-UserComment=", "-overwrite_original"]
            if original:
                args = [f"-Comment={original}", "-UserComment=", "-overwrite_original"]
            else:
                args = ["-Comment=", "-UserComment=", "-overwrite_original"]
            result = subprocess.run(["exiftool"] + args + [file_path],
                                    capture_output=True, encoding='latin-1', errors='replace')
            return result.returncode == 0
        print(f"\n{display.red}[!] ExifTool required for WEBP metadata removal.")
        return False

    if ext == ".pdf":
        return pdf_handler.remove_message(file_path)

    print(f"\n{display.red}[!] Unsupported format for metadata removal: {ext or '(no extension)'}")
    return False

def _ext(file_path: str) -> str:
    """Normalise file extension to lowercase."""
    return os.path.splitext(file_path)[1].lower()


def _exiftool_strip_all(file_path: str) -> None:
    """Best-effort ExifTool full metadata strip; ignores errors."""
    if shutil.which("exiftool"):
        subprocess.run(
            ["exiftool", "-all=", "-overwrite_original", file_path],
            capture_output=True
        )


VERSION = "1.0.1"
