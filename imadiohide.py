import os
import wave
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
from PIL import Image

console = Console()

# ──────────────────────────────
# Utilities & Banner
# ──────────────────────────────
def show_banner():
    # Added 'r' before the string to make it a raw string (Fixes SyntaxWarning)
    banner_text = Text(r"""
  ___ __  __    _   ___ ___ ___  _  _ ___ ___  ___ 
 |_ _|  \/  |  /_\ |   \_ _/ _ \| || |_ _|   \| __|
  | || |\/| | / _ \| |) | | (_) | __ || || |) | _| 
 |___|_|  |_|/_/ \_\___/___\___/|_||_|___|___/|___|
    """, style="bold cyan")

    console.print(
        Panel(
            banner_text,
            title="✨ IMADIOHIDE ✨",
            subtitle="Image & Audio Steganography Tool",
            border_style="bright_magenta",
            box=box.DOUBLE,
            expand=False
        )
    )

def check_file(path):
    if not os.path.exists(path):
        console.print(f"[bold red]❌ Error:[/bold red] File not found at {path}")
        return False
    return True

def string_to_bin(message):
    return ''.join(format(ord(i), '08b') for i in message)

def bin_to_string(binary_data):
    all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
    return decoded_data

# Delimiter to mark the end of the message
DELIMITER = "#####END#####"

# ──────────────────────────────
# 1. Image Steganography
# ──────────────────────────────
def encode_image():
    console.print("\n[bold cyan]🖼️  Hide Text into Image[/bold cyan]")
    img_path = console.input("📁 Enter source image path (PNG recommended): ").strip('"').strip("'")
    
    if not check_file(img_path): return

    message = console.input("💬 Enter secret message: ")
    message += DELIMITER # Add delimiter
    
    try:
        img = Image.open(img_path)
        # Convert to RGB to ensure consistency
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        encoded = img.copy()
        width, height = img.size
        
        binary_message = string_to_bin(message)
        data_len = len(binary_message)
        
        if data_len > width * height * 3:
            console.print("[bold red]❌ Error:[/bold red] Image is too small to hold this message!")
            return

        index = 0
        for y in range(height):
            if index >= data_len: break
            for x in range(width):
                if index >= data_len: break
                pixel = list(img.getpixel((x, y)))
                
                for n in range(3): 
                    if index < data_len:
                        pixel[n] = pixel[n] & ~1 | int(binary_message[index])
                        index += 1
                
                encoded.putpixel((x, y), tuple(pixel))

        base, ext = os.path.splitext(img_path)
        new_path = f"{base}_hidden.png"
        encoded.save(new_path, "PNG")
        console.print(f"\n✅ Message hidden! Saved as: [bold green]{new_path}[/bold green]")
        console.print("[dim]Note: Always use PNG for steganography to prevent data loss.[/dim]")

    except Exception as e:
        console.print(f"[bold red]❌ Error encoding image:[/bold red] {e}")

def decode_image():
    console.print("\n[bold cyan]🖼️  Extract Text from Image[/bold cyan]")
    img_path = console.input("📁 Enter encoded image path: ").strip('"').strip("'")
    
    if not check_file(img_path): return

    try:
        img = Image.open(img_path)
        binary_data = ""
        
        for y in range(img.height):
            for x in range(img.width):
                pixel = img.getpixel((x, y))
                for n in range(3):
                    binary_data += str(pixel[n] & 1)

        decoded_message = ""
        all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
        
        found = False
        for byte in all_bytes:
            char = chr(int(byte, 2))
            decoded_message += char
            if decoded_message.endswith(DELIMITER):
                decoded_message = decoded_message[:-len(DELIMITER)]
                found = True
                break
        
        if found:
            console.print(f"\n🕵️  Hidden Message: [bold yellow]{decoded_message}[/bold yellow]")
        else:
            console.print("\n[bold red]❌ No hidden message found or incorrect format.[/bold red]")

    except Exception as e:
        console.print(f"[bold red]❌ Error decoding image:[/bold red] {e}")

# ──────────────────────────────
# 2. Audio Steganography
# ──────────────────────────────
def encode_audio():
    console.print("\n[bold cyan]🎵 Hide Text into Audio (WAV)[/bold cyan]")
    audio_path = console.input("📁 Enter source audio path (.wav): ").strip('"').strip("'")
    
    if not check_file(audio_path): return

    message = console.input("💬 Enter secret message: ")
    message += DELIMITER

    try:
        song = wave.open(audio_path, mode='rb')
        frame_bytes = bytearray(list(song.readframes(song.getnframes())))
        
        binary_message = string_to_bin(message)
        
        if len(binary_message) > len(frame_bytes):
            console.print("[bold red]❌ Error:[/bold red] Audio file is too short for this message.")
            song.close()
            return
        
        for i in range(len(binary_message)):
            frame_bytes[i] = (frame_bytes[i] & 254) | int(binary_message[i])
            
        base, ext = os.path.splitext(audio_path)
        new_path = f"{base}_hidden.wav"
        
        frame_modified = bytes(frame_bytes)
        with wave.open(new_path, 'wb') as new_song:
            new_song.setparams(song.getparams())
            new_song.writeframes(frame_modified)
            
        song.close()
        console.print(f"\n✅ Message hidden! Saved as: [bold green]{new_path}[/bold green]")

    except Exception as e:
        console.print(f"[bold red]❌ Error encoding audio:[/bold red] {e}")

def decode_audio():
    console.print("\n[bold cyan]🎵 Extract Text from Audio[/bold cyan]")
    audio_path = console.input("📁 Enter encoded audio path (.wav): ").strip('"').strip("'")
    
    if not check_file(audio_path): return

    try:
        song = wave.open(audio_path, mode='rb')
        frame_bytes = bytearray(list(song.readframes(song.getnframes())))
        
        extracted_text = ""
        temp_bin = ""
        found = False
        
        for i in range(len(frame_bytes)):
            temp_bin += str(frame_bytes[i] & 1)
            
            if len(temp_bin) == 8:
                char = chr(int(temp_bin, 2))
                extracted_text += char
                temp_bin = ""
                
                if extracted_text.endswith(DELIMITER):
                    extracted_text = extracted_text[:-len(DELIMITER)]
                    found = True
                    break
        
        song.close()
        
        if found:
            console.print(f"\n🕵️  Hidden Message: [bold yellow]{extracted_text}[/bold yellow]")
        else:
            console.print("\n[bold red]❌ No hidden message found or file is too large/corrupted.[/bold red]")

    except Exception as e:
        console.print(f"[bold red]❌ Error decoding audio:[/bold red] {e}")

# ──────────────────────────────
# Menus
# ──────────────────────────────
def image_menu():
    while True:
        console.print("\n[bold white]--- Image Steganography ---[/bold white]")
        console.print("[1] Hide text into Image")
        console.print("[2] Extract text from Image")
        console.print("[3] Back to Main Menu")
        
        choice = console.input("[cyan]Select option: [/cyan]")
        
        if choice == "1": encode_image()
        elif choice == "2": decode_image()
        elif choice == "3": break
        else: console.print("[red]Invalid choice![/red]")

def audio_menu():
    while True:
        console.print("\n[bold white]--- Audio Steganography ---[/bold white]")
        console.print("[1] Hide text into Audio")
        console.print("[2] Extract text from Audio")
        console.print("[3] Back to Main Menu")
        
        choice = console.input("[cyan]Select option: [/cyan]")
        
        if choice == "1": encode_audio()
        elif choice == "2": decode_audio()
        elif choice == "3": break
        else: console.print("[red]Invalid choice![/red]")

def main():
    show_banner()
    while True:
        console.print("\n[bold magenta]MAIN MENU[/bold magenta]")
        console.print("[1] Image Steganography")
        console.print("[2] Audio Steganography")
        console.print("[3] Exit")

        choice = console.input("\n[bold white]Enter your choice:[/bold white] ")

        if choice == "1":
            image_menu()
        elif choice == "2":
            audio_menu()
        elif choice == "3":
            console.print("\n👋 Goodbye!", style="bold red")
            break
        else:
            console.print("[red]Invalid choice![/red]")

if __name__ == "__main__":
    main()
