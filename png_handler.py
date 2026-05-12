"""
png_handler.py, Manipulador de metadados PNG de baixo nível e não destrutivo.

Princípio de design: operar diretamente no fluxo de blocos PNG.

Nunca chamamos o método Image.save() do Pillow, que recodificaria os dados IDAT
e alteraria os parâmetros de compressão, os bytes de filtro e a ordem dos blocos auxiliares.

Estrutura PNG:

Assinatura de 8 bytes
N × blocos: [comprimento de 4B][tipo de 4B][dados NB][CRC32 de 4B]

Analisamos apenas o envelope do bloco. Os dados IDAT são transmitidos sem alterações.

Apenas os blocos tEXt/iTXt que contêm nosso marcador são inseridos ou removidos.

Todos os outros blocos (incluindo PLTE, gAMA, cHRM, sRGB, iCCP, pHYs, etc.)
são preservados literalmente, ou seja, seus bytes nunca são recalculados.
"""

import struct
import zlib
import os
import shutil
import tempfile

PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'
MARKER_KEY = b'zstge' 
CHUNK_TYPE_TEXT = b'tEXt'
CHUNK_TYPE_IEND = b'IEND'
CHUNK_TYPE_IHDR = b'IHDR'


def _crc32(chunk_type: bytes, data: bytes) -> int:
    return zlib.crc32(chunk_type + data) & 0xFFFFFFFF


def _pack_chunk(chunk_type: bytes, data: bytes) -> bytes:
    length = struct.pack('>I', len(data))
    crc = struct.pack('>I', _crc32(chunk_type, data))
    return length + chunk_type + data + crc


def _read_chunks(data: bytes):
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("Not a valid PNG file (bad signature)")

    pos = 8 
    while pos < len(data):
        if pos + 8 > len(data):
            raise ValueError(f"Truncated PNG at byte {pos}")
        length = struct.unpack('>I', data[pos:pos + 4])[0]
        chunk_type = data[pos + 4:pos + 8]
        chunk_data = data[pos + 8:pos + 8 + length]
        raw = data[pos:pos + 12 + length]
        pos += 12 + length
        yield chunk_type, chunk_data, raw


def _is_our_text_chunk(chunk_type: bytes, chunk_data: bytes) -> bool:
    if chunk_type != CHUNK_TYPE_TEXT:
        return False
    null_pos = chunk_data.find(b'\x00')
    if null_pos == -1:
        return False
    keyword = chunk_data[:null_pos]
    return keyword == MARKER_KEY

def insert_message(file_path: str, message: str) -> bool:
    try:
        with open(file_path, 'rb') as f:
            original = f.read()

        chunks = list(_read_chunks(original))

        text_data = MARKER_KEY + b'\x00' + message.encode('latin-1', errors='replace')
        new_chunk_raw = _pack_chunk(CHUNK_TYPE_TEXT, text_data)

        out_parts = [PNG_SIGNATURE]
        injected = False

        for chunk_type, chunk_data, raw in chunks:
            if _is_our_text_chunk(chunk_type, chunk_data):
                continue

            out_parts.append(raw)

            if chunk_type == CHUNK_TYPE_IHDR and not injected:
                out_parts.append(new_chunk_raw)
                injected = True

        if not injected:
            raise RuntimeError("IHDR chunk not found — invalid PNG structure")

        _atomic_write(file_path, b''.join(out_parts))
        return True

    except Exception as e:
        import display
        print(f"\n{display.red}[!] PNG insert error: {e}")
        return False


def remove_message(file_path: str) -> bool:
    try:
        with open(file_path, 'rb') as f:
            original = f.read()

        out_parts = [PNG_SIGNATURE]
        removed = 0

        for chunk_type, chunk_data, raw in _read_chunks(original):
            if _is_our_text_chunk(chunk_type, chunk_data):
                removed += 1
                continue     
            out_parts.append(raw)

        if removed == 0:
            return False    
          
        _atomic_write(file_path, b''.join(out_parts))
        return True

    except Exception as e:
        import display
        print(f"\n{display.red}[!] PNG remove error: {e}")
        return False


def list_text_chunks(file_path: str) -> list[tuple[str, str]]:
    results = []
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        for chunk_type, chunk_data, _ in _read_chunks(data):
            if chunk_type == CHUNK_TYPE_TEXT:
                null_pos = chunk_data.find(b'\x00')
                if null_pos != -1:
                    keyword = chunk_data[:null_pos].decode('latin-1', errors='replace')
                    text = chunk_data[null_pos + 1:].decode('latin-1', errors='replace')
                    results.append((keyword, text))
    except Exception:
        pass
    return results


def _atomic_write(file_path: str, data: bytes) -> None:
    dir_name = os.path.dirname(os.path.abspath(file_path))
    fd, tmp_path = tempfile.mkstemp(dir=dir_name)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
        shutil.move(tmp_path, file_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
