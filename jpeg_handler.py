"""
jpeg_handler.py - Manipulador não destrutivo de metadados JPEG.

Princípio de design: usar o piexif para correção de segmentos EXIF ​​no local.

O piexif.insert() insere apenas o segmento APP1/EXIF, deixando todos os
outros marcadores JPEG (SOI, APP0/JFIF, SOS, dados de varredura, EOI) intactos.

O Pillow Image.save() é evitado deliberadamente: ele recodifica os dados de varredura,
altera as tabelas de quantização e redefine todos os EXIF, a menos que sejam explicitamente
preservados — tudo isso é indesejável do ponto de vista forense.

Estratégia de segurança contra sobrescrita
-----------------------
A tag Software pode já conter um valor que o usuário não inseriu
(por exemplo, a string do firmware da câmera ou a assinatura de um editor). Excluí-la cegamente
em remove() deixaria o arquivo em um estado diferente do
antes da inserção — exatamente a deriva que queremos evitar.

Solução: no momento da inserção, lemos o valor atual do Software e o armazenamos no campo UserComment do EXIF ​​sob um prefixo sentinela zstge.

No momento da remoção, lemos esse sentinela de volta e restauramos o Software ao seu valor original (ou excluímos o campo se ele estava ausente antes de o modificarmos).

Formato do sentinela armazenado em UserComment:

b"zstge\x00<bytes_or_vazio_original_do_software>"

Inclusive, o campo UserComment foi escolhido porque:

- Raramente é usado por câmeras ou editores para dados relevantes.

- Ele sobrevive a conversões de ida e volta do PEXIF sem problemas.

- Ele é claramente identificado pelo nosso prefixo, evitando confusões com conteúdo preexistente.


Se o UserComment já contiver dados que não sejam zstge, interrompemos a operação com um erro em vez de sobrescrevê-lo, evitando qualquer perda de dados.
"""

import shutil
import subprocess

try:
    import piexif
    _PIEXIF_AVAILABLE = True
except ImportError:
    _PIEXIF_AVAILABLE = False

_SENTINEL = b"zstge\x00"
_EXIFTOOL_SENTINEL_TAG = "UserComment"

def _exiftool_available() -> bool:
    return shutil.which("exiftool") is not None


def _run_exiftool(args: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["exiftool"] + args,
            capture_output=True,
            encoding='latin-1', errors='replace'
        )
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)

def insert_message(file_path: str, message: str) -> bool:
    if _PIEXIF_AVAILABLE:
        return _piexif_insert(file_path, message)
    elif _exiftool_available():
        return _exiftool_insert(file_path, message)
    else:
        _print_err("Neither piexif nor ExifTool is available for JPEG insertion.")
        return False


def remove_message(file_path: str) -> bool:
    if _PIEXIF_AVAILABLE:
        return _piexif_remove(file_path)
    elif _exiftool_available():
        return _exiftool_remove(file_path)
    else:
        _print_err("Neither piexif nor ExifTool is available for JPEG metadata removal.")
        return False


def remove_all_metadata(file_path: str) -> bool:
    if _exiftool_available():
        ok, msg = _run_exiftool(["-all=", "-overwrite_original", file_path])
        if not ok:
            _print_err(f"ExifTool removal failed: {msg}")
        return ok
    if _PIEXIF_AVAILABLE:
        try:
            piexif.remove(file_path)
            return True
        except Exception as e:
            _print_err(f"piexif removal failed: {e}")
            return False
    _print_err("No suitable tool available for full JPEG metadata removal.")
    return False

def _piexif_insert(file_path: str, message: str) -> bool:
    try:
        try:
            exif_dict = piexif.load(file_path)
        except Exception:
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}

        existing_comment = exif_dict.get("Exif", {}).get(piexif.ExifIFD.UserComment, b"")
        if existing_comment.startswith(_SENTINEL):
            _print_err("A zstge message is already embedded. Remove it first.")
            return False

        if existing_comment and not existing_comment.startswith(_SENTINEL):
            _print_err(
                "UserComment already contains data not written by zstge. "
                "Cannot safely use it as a sentinel store."
            )
            return False

        original_software = exif_dict.get("0th", {}).get(piexif.ImageIFD.Software, b"")
        if isinstance(original_software, str):
            original_software = original_software.encode("utf-8")

        sentinel_payload = _SENTINEL + original_software
        exif_dict.setdefault("Exif", {})[piexif.ExifIFD.UserComment] = sentinel_payload
      
        exif_dict.setdefault("0th", {})[piexif.ImageIFD.Software] = message.encode("utf-8")

        piexif.insert(piexif.dump(exif_dict), file_path)
        return True
    except Exception as e:
        _print_err(f"piexif insert failed: {e}")
        return False


def _piexif_remove(file_path: str) -> bool:
    try:
        exif_dict = piexif.load(file_path)

        sentinel = exif_dict.get("Exif", {}).get(piexif.ExifIFD.UserComment, b"")
        if not sentinel.startswith(_SENTINEL):
            return True 

        original_software = sentinel[len(_SENTINEL):] 

  
        if original_software:
            exif_dict.setdefault("0th", {})[piexif.ImageIFD.Software] = original_software
        else:
            exif_dict.get("0th", {}).pop(piexif.ImageIFD.Software, None)


        exif_dict.get("Exif", {}).pop(piexif.ExifIFD.UserComment, None)

        piexif.insert(piexif.dump(exif_dict), file_path)
        return True
    except Exception as e:
        _print_err(f"piexif remove failed: {e}")
        return False


def _exiftool_insert(file_path: str, message: str) -> bool:
    _, current = _run_exiftool(["-Software", "-b", file_path])
    original = current.strip()  

    _, existing_comment = _run_exiftool(["-UserComment", "-b", file_path])
    if existing_comment.startswith("zstge\x00"):
        _print_err("A zstge message is already embedded. Remove it first.")
        return False

    sentinel_value = f"zstge\x00{original}"

    ok, msg = _run_exiftool([
        f"-Software={message}",
        f"-UserComment={sentinel_value}",
        "-overwrite_original",
        file_path
    ])
    if not ok:
        _print_err(f"ExifTool insert failed: {msg}")
    return ok


def _exiftool_remove(file_path: str) -> bool:
    _, comment = _run_exiftool(["-UserComment", "-b", file_path])
    if not comment.startswith("zstge\x00"):
        return True 

    original_software = comment[len("zstge\x00"):]

    args = ["-UserComment=", "-overwrite_original"]
    if original_software:
        args = [f"-Software={original_software}", "-UserComment=", "-overwrite_original"]
    else:
        args = ["-Software=", "-UserComment=", "-overwrite_original"]

    ok, msg = _run_exiftool(args + [file_path])
    if not ok:
        _print_err(f"ExifTool remove failed: {msg}")
    return ok


def _print_err(msg: str) -> None:
    try:
        import display
        print(f"\n{display.red}[!] {msg}")
    except ImportError:
        print(f"[!] {msg}")
