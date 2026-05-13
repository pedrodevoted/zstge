<h1 align="center">zstge</h1><p align="center">
  A forensic-oriented CLI utility for metadata inspection, lightweight steganography and structural integrity-aware workflows.
</p><p align="center">
  <img src="https://img.shields.io/badge/type-CLI-green">
  <img src="https://img.shields.io/badge/python-3.8+-blue">
  <img src="https://img.shields.io/badge/license-MIT-red">
</p>

## Overview

zstge is a Linux-oriented command-line utility focused on:

- metadata inspection
- metadata removal
- lightweight steganography
- structural integrity-aware workflows

The project began as a simple metadata utility and gradually evolved into a deeper exploration of forensic-friendly file handling and non-destructive metadata operations.

---

## Philosophy

Many metadata tools are either:

- too opaque
- too destructive
- or too cumbersome for fast terminal workflows

"zstge" is designed around a different approach:

- predictable behavior
- explicit output
- modular tooling
- Unix-friendly workflows
- non-destructive-by-default operations

The goal is not to replace mature tooling like ExifTool, but to provide a more direct and controlled interface for common metadata workflows.

---

## Structural Integrity & Forensic Mindset

One of the main goals of "zstge" is minimizing unintended file modifications during metadata operations.

A key design principle of the project is:

_removing metadata does not necessarily restore the original file state_

Many high-level libraries fully rewrite files during simple operations, unintentionally altering:

- internal structure
- metadata layout
- PNG chunks
- compression behavior
- auxiliary metadata
- binary signatures

To reduce metadata drift and structural inconsistencies, "zstge" adopts format-aware workflows whenever possible.

Current integrity-oriented approaches include:

- localized PNG chunk handling
- minimized file rewriting
- ExifTool integration for safer metadata operations
- modular format-specific handlers
- explicit scan validation before/after operations

---

## Features

- Metadata inspection for 130+ formats (via ExifTool)
- Lightweight hidden-message embedding
- Metadata removal workflows
- PNG/JPEG/PDF support
- Interactive menu interface
- Argument-based CLI mode
- Explicit error handling
- Linux-oriented workflows
- Modular architecture for format handlers

---

## Technical Highlights

The project explores concepts such as:

- metadata analysis
- binary file handling
- localized patching
- subprocess/tool integration
- format-aware processing
- structural integrity preservation
- forensic-oriented workflows
- CLI tooling architecture

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
---


License

This project is licensed under the MIT License © 2026 pedrodevoted
