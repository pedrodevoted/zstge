import os
import sys
import utils
import shutil
import display
import argparse
from InquirerPy import prompt
from pystyle import Anime, Colorate, Colors, Center

logo = """
                     █████                     
                    ▒▒███                      
  █████████  █████  ███████    ███████  ██████ 
 ▒█▒▒▒▒███  ███▒▒  ▒▒▒███▒    ███▒▒███ ███▒▒███
 ▒   ███▒  ▒▒█████   ▒███    ▒███ ▒███▒███████ 
   ███▒   █ ▒▒▒▒███  ▒███ ███▒███ ▒███▒███▒▒▒  
  █████████ ██████   ▒▒█████ ▒▒███████▒▒██████ 
 ▒▒▒▒▒▒▒▒▒ ▒▒▒▒▒▒     ▒▒▒▒▒   ▒▒▒▒▒███ ▒▒▒▒▒▒  
                              ███ ▒███         
                             ▒▒██████          
                              ▒▒▒▒▒▒           """

logoI = """
⠀⠀⠀⣰⣟⠲⠤⣤⣤⣤⠶⢖⣲⣶⡶⢶⣶⣖⡲⠶⣤⣤⣤⡤⠖⡛⣆⠀⠀⠀
⠀⠀⠀⡏⣿⣷⣄⠀⡟⢡⡶⠛⠉⠁⠀⠀⠈⠉⠛⢶⡌⠻⠀⣠⣾⣿⢹⠀⠀⠀
⠀⠀⠀⡇⢹⣿⣿⠆⣠⠞⢁⣀⣠⣤⡴⢦⣤⣄⣀⡈⠳⣄⢰⣿⣿⣟⢸⡄⠀⠀
⠀⠀⠀⢻⣤⡻⠁⡸⢃⠜⠋⠉⠉⣠⠀⠐⣄⠉⠉⠙⠢⡘⢧⡙⣿⣣⡿⠀⠀⠀
⠀⠀⢀⣾⡷⠁⠊⠀⠀⠤⠖⠋⠉⠑⡀⢀⠊⠉⠙⠲⠤⠀⠀⠑⠀⢾⣷⡄⠀⠀
⠀⠀⣴⡿⠃⠀⡀⣀⡴⠁⣤⠶⠚⠋⠀⠀⠙⠓⠶⣤⠈⢦⣀⢀⠀⠘⢿⣦⠀⠀
⢀⣾⠏⠀⣰⡟⢰⢏⣀⡐⠁⠀⠀⠀⠀⠀⠀⠀⡀⠈⢂⣀⡙⡆⢻⣆⠀⠹⣷⡀
⣼⡏⠀⠀⣿⣧⠸⠀⠻⣏⠟⣾⣄⠀⠀⠀⠀⣠⣷⠻⣹⠟⠀⠇⣼⣷⡀⠀⢹⣷
⣿⣰⠀⠀⣿⣿⡇⠀⠀⠉⠉⢹⣿⠀⠀⠀⠀⣿⡏⠉⠉⠀⠀⢸⣿⣿⠁⠀⣆⣿
⢻⢿⣠⠀⠀⣿⣯⠁⠀⠀⢀⡞⠀⠀⠀⠀⠀⠈⢷⡀⠀⠀⠊⣽⣿⠁⠀⡀⡿⡟
⠈⢸⣿⡆⡀⠈⢿⣇⡀⠀⡼⢰⠀⠀⠀⠀⠀⠀⡏⢧⠀⢀⣸⡿⠃⢀⢰⣿⡗⠀
⠀⠈⢿⢿⣿⣦⡈⠻⢿⣄⡁⡾⠀⠀⠀⠀⠀⠀⢷⢈⣠⡿⠟⢁⣴⣿⡿⡻⠁⠀
⠀⠀⠀⠈⠻⠟⢿⣶⣤⣿⢇⢳⡀⠀⠀⠀⠀⢀⡞⡸⣿⣤⣶⡿⠻⠟⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣘⣿⣒⣂⠙⠛⢷⡾⠛⠋⢐⣒⣿⣓⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠚⣧⣖⣀⣀⣬⣧⣀⣀⣲⣽⠃⠒⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠳⢤⣄⣠⡤⠾⠛⠉"""

intro = f"""
{logoI}
> Press Enter
"""

def center_text(text: str) -> str:
    width = shutil.get_terminal_size((80, 20)).columns
    return text.center(width)

def show_logo():
    os.system("clear")
    print(Colorate.Horizontal(Colors.yellow_to_red, Center.XCenter(logo)))

def run_argument_mode():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-s", "--scan", help="Path to file to scan or embed message")
    parser.add_argument("-m", "--message", help="Message to hide (used with -s)")
    parser.add_argument("-r", "--remove", help="Path to file to remove metadata")
    parser.add_argument("-h", "--help", action="store_true", help="Show help and valid formats")
    args = parser.parse_args()

    if args.help:
        print(Colorate.Horizontal(Colors.yellow_to_red, Center.XCenter(logo)))
        print(f"""
Usage:
  python zstge.py -s {display.yellow}<file>{display.white}               Scan metadata
  python zstge.py -s {display.yellow}<file>{display.white} -m {display.yellow}<message>{display.white}  Hide message in file (steganography)
  python zstge.py -r {display.yellow}<file>{display.white}               Remove metadata from file
  python zstge.py -h                      Show this help and info

Supported formats for {display.byellow}scan{display.white} (via ExifTool): JPG, JPEG, PNG, PDF, WEBP, MP4, MP3, DOCX, XLSX, PPTX, JSON, ZIP, and 100+ others.
Supported formats for {display.byellow}hide and remove metadata{display.white}: JPG, PNG, WEBP, PDF

Notes:
  PNG  — message embedded as a tEXt chunk; IDAT image data is never modified.
  JPEG — message written to EXIF Software tag via piexif/ExifTool; no re-encoding.
  PDF  — message written to /Title via ExifTool incremental update (preferred) or pypdf.
  WEBP — metadata edited via ExifTool; requires ExifTool in PATH.
        """)
        return

    if args.scan and args.message:
        if os.path.isfile(args.scan):
            if utils.hide_message(args.scan, args.message):
                print(f"\n{display.green}[+] Message successfully hidden in {args.scan} !{display.white}")
        else:
            print(f"{display.red}[!] File not found: {args.scan}")
        return

    if args.scan:
        if os.path.isfile(args.scan):
            print(Colorate.Horizontal(Colors.yellow_to_red, Center.XCenter(logo)))
            utils.scan_image_metadata(args.scan)
        else:
            print(f"{display.red}[!] File not found: {args.scan}")
        return

    if args.remove:
        if os.path.isfile(args.remove):
            if utils.remove_metadata(args.remove):
                print(f"\n{display.green}[+] Metadata successfully removed from {args.remove} !{display.white}")
        else:
            print(f"{display.red}[!] File not found: {args.remove}")
        return

    print(f"{display.yellow}[!] Invalid or missing arguments. Use -h for help or run without args for menu.")

def run_menu():
    Anime.Fade(Center.Center(intro), Colors.yellow_to_red, Colorate.Horizontal, interval=0.0025, enter=True)
    while True:
        show_logo()
        questions = [
            {
                "type": "list",
                "name": "choice",
                "message": center_text("Select an option"),
                "choices": [
                    center_text("1. Hide Message"),
                    center_text("2. Scan Metadata"),
                    center_text("3. Remove Metadata"),
                    center_text("4. Info"),
                    center_text("5. Exit")
                ]
            }
        ]

        answers = prompt(questions, style={
            "question": "fg:ansiyellow bold",
            "pointer": "fg:ansiyellow",
            "highlight": "fg:ansired bold",
            "answer": "fg:ansiyellow bold",
        })

        choice = answers["choice"].strip()
        show_logo()

        if choice.startswith("1"):
            os.system('clear')
            print(Colorate.Horizontal(Colors.yellow_to_red, Center.XCenter(logo)))
            file_path = input(f"\n{display.bwhite}[{display.byellow}>{display.bwhite}]{display.white} Enter the path to the file: ")
            message_to_hide = input(f"{display.bwhite}[{display.byellow}>{display.bwhite}]{display.white} Enter the message to be hidden: ")
            if utils.hide_message(file_path, message_to_hide):
                print(f"\n{display.green}[+] Message successfully hidden in {file_path} !{display.white}")
            input(f"\n{display.white}Press {display.bwhite}[ENTER]{display.white} to continue")

        elif choice.startswith("2"):
            os.system('clear')
            print(Colorate.Horizontal(Colors.yellow_to_red, Center.XCenter(logo)))
            file_path = input(f"\n{display.bwhite}[{display.byellow}>{display.bwhite}]{display.white} Enter the path of the file to scan: ")
            utils.scan_image_metadata(file_path)
            input(f"\n{display.white}Press {display.bwhite}[ENTER]{display.white} to return to menu")

        elif choice.startswith("3"):
            os.system('clear')
            print(Colorate.Horizontal(Colors.yellow_to_red, Center.XCenter(logo)))
            file_path = input(f"\n{display.bwhite}[{display.byellow}>{display.bwhite}]{display.white} Enter the path of the file to remove metadata: ")
            if utils.remove_metadata(file_path):
                print(f"\n{display.green}[+] Metadata successfully removed from {file_path} !{display.white}")
            input(f"\n{display.white}Press {display.bwhite}[ENTER]{display.white} to return to menu")

        elif choice.startswith("4"):
            os.system('clear')
            print(Colorate.Horizontal(Colors.yellow_to_red, Center.XCenter(logo)))
            print(
                f"\nSupported formats for {display.byellow}scan{display.white} (via ExifTool): "
                "JPG, JPEG, PNG, PDF, WEBP, MP4, MP3, DOCX, XLSX, PPTX, JSON, ZIP, and 100+ others.\n"
                f"Supported formats for {display.byellow}hide and remove metadata{display.white}: JPG, PNG, WEBP, PDF\n\n"
                f"{display.bwhite}PNG{display.white}  — tEXt chunk injection after IHDR; IDAT never touched.\n"
                f"{display.bwhite}JPEG{display.white} — EXIF Software tag patched; no scan data re-encoding.\n"
                f"{display.bwhite}PDF{display.white}  — /Title via ExifTool incremental update (preferred) or pypdf fallback.\n"
                f"{display.bwhite}WEBP{display.white} — XMP Comment tag via ExifTool (requires ExifTool).\n\n"
                f"{display.bwhite}Zstge is built for metadata testing and steganography research.\n"
                f"Project: https://github.com/pedrodevoted/zstge"
            )
            input(f"\n{display.white}Press {display.bwhite}[ENTER]{display.white} to return to menu")

        elif choice.startswith("5"):
            os.system('clear')
            print(Colorate.Horizontal(Colors.yellow_to_red, Center.XCenter(logoI)))
            print(f"\n{display.byellow}Until next time.")
            sys.exit()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_argument_mode()
    else:
        run_menu()
