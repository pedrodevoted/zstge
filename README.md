<p align="center">
  <img src="images/image.png" width="220" />
</p>

<p align="center">
  A practical CLI tool for steganography and metadata inspection.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/type-CLI-green">
  <img src="https://img.shields.io/badge/python-3.8+-blue">
  <img src="https://img.shields.io/badge/license-MIT-red">
</p>

---

## Overview

**zstge** is a command-line utility focused on **metadata analysis and lightweight steganography**.

It does one thing well:
- inspect metadata
- remove metadata
- embed simple hidden messages

---

## Why zstge?

Most tools are either:
- too bloated  
- too opaque  
- or too fragile for daily use  

**zstge** is built with a forensic mindset:
- predictable behavior  
- explicit output  
- non-destructive by default  

It is designed for analysts, students, and anyone who prefers **tools over toys**.

---

## Features

- Scan metadata from **130+ file formats** (via ExifTool)
- Embed hidden messages into:
  - PNG
  - JPG / JPEG
  - WEBP
  - PDF
- Remove metadata cleanly from supported formats
- Dual interface:
  - interactive menu
  - argument-based CLI
- Clear error handling and safe file operations

---

## Install
> [!NOTE]
> For the installation to work, you must have git installed previously.
```
git clone https://github.com/pedrodevoted/zstge/
```
```
cd zstge
```
```
bash install
```
## Start in menu mode (recommended for beginners)
Use the command ↓ to start the python virtual environment
```
source zstge_env/bin/activate
```
And use ↓ to start
```
python3 zstge.py
```
After use, the user ↓ to close the virtual environment (recommended)
```
deactivate
```
---

## Start in argument mode (recommended for experienced)
Use the command ↓ to start the python virtual environment
```
source zstge_env/bin/activate
```
And use ↓ to get the list of arguments
```
python3 zstge.py -h
```
After use, the user ↓ to close the virtual environment (recommended)
```
deactivate
```
## License
This project is licensed under the MIT License © 2026 pedrodevoted
---
