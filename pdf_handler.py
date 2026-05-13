"""
pdf_handler.py - Manipulador de metadados de PDF minimamente destrutivo.

Os metadados de PDF residem em dois locais:

1. Dicionário de Informações do Documento (/Info) (mais antigo, amplamente suportado)
2. Fluxo de metadados XMP (/Metadata) (moderno, mais rico)

Restrições de projeto
------------------
O PyPDF2/pypdf reescreve toda a tabela de referência cruzada e re-serializa
todos os objetos de página ao gravar um arquivo, o que altera os deslocamentos de bytes,
a numeração de objetos e a estrutura geral do PDF. Isso é inevitável
ao usar apenas o PyPDF2, não existe uma API de "patch in-place" verdadeira.

Estratégia preferida: ExifTool

O ExifTool grava uma atualização incremental (anexada aos bytes originais do PDF)
ao modificar os metadados do PDF. Isso preserva o corpo original
literalmente e apenas anexa uma pequena seção de atualização com novos objetos /Info ou XMP.

As ferramentas forenses ainda encontrarão a estrutura original do documento
intacta na parte anterior do arquivo.

Estratégia de fallback: pypdf (sucessor do PyPDF2, mesma limitação de reescrita)

Se o ExifTool não estiver disponível, usamos pypdf / PyPDF2 e documentamos a
limitação explicitamente. Ainda minimizamos os danos:

- copiando objetos de página sem descompressão
- atualizando apenas o dicionário /Info, não o fluxo XMP
- mantendo o caminho do código de fallback o mais enxuto possível

Nota sobre a limitação
---------------
Essa correção direta do /Info do PDF sem reescrever a tabela xref
requer um gravador de atualização incremental personalizado (adicionando %%EOF e uma nova
seção xref). Isso está além da API do PyPDF2. O ExifTool fornece isso
de forma confiável, então o usamos como o caminho principal. O fallback deve ser
tratado apenas como uma conveniência, não como equivalente forense. Então pode fazer sentido eu voltar aqui numa próxima atualização...
"""

import os
import shutil
import subprocess
import tempfile

try:
    from pypdf import PdfReader, PdfWriter
    _PYPDF_AVAILABLE = True
except ImportError:
    try:
        from PyPDF2 import PdfReader, PdfWriter
        _PYPDF_AVAILABLE = True
    except ImportError:
        _PYPDF_AVAILABLE = False

_SENTINEL_PREFIX = "zstge\x00"


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
    if _exiftool_available():
        return _exiftool_set_title(file_path, message)
    elif _PYPDF_AVAILABLE:
        _warn_rewrite("insertion")
        return _pypdf_set_title(file_path, message)
    else:
        _print_err("Neither ExifTool nor pypdf is available for PDF insertion.")
        return False


def remove_message(file_path: str) -> bool:
    if _exiftool_available():
        return _exiftool_restore_title(file_path)
    elif _PYPDF_AVAILABLE:
        _warn_rewrite("removal")
        return _pypdf_restore_title(file_path)
    else:
        _print_err("No suitable tool available for PDF metadata removal.")
        return False


def remove_all_metadata(file_path: str) -> bool:
    if _exiftool_available():
        ok, msg = _run_exiftool(["-all=", "-overwrite_original", file_path])
        if not ok:
            _print_err(f"ExifTool PDF metadata removal failed: {msg}")
        return ok
    if _PYPDF_AVAILABLE:
        _warn_rewrite("full metadata removal")
        return _pypdf_set_metadata(file_path, {})
    _print_err("No suitable tool available for full PDF metadata removal.")
    return False


def _exiftool_set_title(file_path: str, title: str) -> bool:
    _, original = _run_exiftool(["-Title", "-b", file_path])
    original = original.strip()

    _, existing_subject = _run_exiftool(["-Subject", "-b", file_path])
    if existing_subject.startswith(_SENTINEL_PREFIX):
        _print_err("A zstge message is already embedded. Remove it first.")
        return False

    sentinel = f"{_SENTINEL_PREFIX}{original}"
    ok, msg = _run_exiftool([
        f"-Title={title}",
        f"-Subject={sentinel}",
        "-overwrite_original",
        file_path
    ])
    if not ok:
        _print_err(f"ExifTool PDF title set failed: {msg}")
    return ok


def _exiftool_restore_title(file_path: str) -> bool:
    _, subject = _run_exiftool(["-Subject", "-b", file_path])
    if not subject.startswith(_SENTINEL_PREFIX):
        return True

    original_title = subject[len(_SENTINEL_PREFIX):]
    if original_title:
        args = [f"-Title={original_title}", "-Subject=", "-overwrite_original"]
    else:
        args = ["-Title=", "-Subject=", "-overwrite_original"]

    ok, msg = _run_exiftool(args + [file_path])
    if not ok:
        _print_err(f"ExifTool PDF title restore failed: {msg}")
    return ok


def _pypdf_set_metadata(file_path: str, meta_dict: dict) -> bool:
    try:
        reader = PdfReader(file_path)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        existing = dict(reader.metadata) if reader.metadata else {}
        existing.update(meta_dict)
        writer.add_metadata(existing)
        _atomic_write_pdf(file_path, writer)
        return True
    except Exception as e:
        _print_err(f"pypdf metadata write failed: {e}")
        return False


def _pypdf_set_title(file_path: str, title: str) -> bool:
    try:
        reader = PdfReader(file_path)
        existing = dict(reader.metadata) if reader.metadata else {}

        current_subject = existing.get("/Subject", "")
        if isinstance(current_subject, str) and current_subject.startswith(_SENTINEL_PREFIX):
            _print_err("A zstge message is already embedded. Remove it first.")
            return False

        original_title = existing.get("/Title", "")
        existing["/Subject"] = f"{_SENTINEL_PREFIX}{original_title}"
        existing["/Title"] = title

        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.add_metadata(existing)
        _atomic_write_pdf(file_path, writer)
        return True
    except Exception as e:
        _print_err(f"pypdf title set failed: {e}")
        return False


def _pypdf_restore_title(file_path: str) -> bool:
    try:
        reader = PdfReader(file_path)
        existing = dict(reader.metadata) if reader.metadata else {}

        subject = existing.get("/Subject", "")
        if not isinstance(subject, str) or not subject.startswith(_SENTINEL_PREFIX):
            return True

        original_title = subject[len(_SENTINEL_PREFIX):]
        existing.pop("/Subject", None)
        if original_title:
            existing["/Title"] = original_title
        else:
            existing.pop("/Title", None)

        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.add_metadata(existing)
        _atomic_write_pdf(file_path, writer)
        return True
    except Exception as e:
        _print_err(f"pypdf title restore failed: {e}")
        return False


def _atomic_write_pdf(file_path: str, writer) -> None:
    dir_name = os.path.dirname(os.path.abspath(file_path))
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".pdf")
    try:
        with os.fdopen(fd, 'wb') as f:
            writer.write(f)
        shutil.move(tmp_path, file_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _print_err(msg: str) -> None:
    try:
        import display
        print(f"\n{display.red}[!] {msg}")
    except ImportError:
        print(f"[!] {msg}")


def _warn_rewrite(operation: str) -> None:
    try:
        import display
        print(
            f"\n{display.yellow}[!] ExifTool not available. "
            f"PDF {operation} will use pypdf (full file rewrite).\n"
            f"    Binary structure will differ from original. "
            f"Install ExifTool for forensic-grade operations.{display.white}"
        )
    except ImportError:
        print(
            f"[!] ExifTool not available. PDF {operation} uses pypdf "
            f"(full rewrite — not forensically equivalent)."
        )
