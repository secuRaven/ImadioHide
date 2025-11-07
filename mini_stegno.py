import os
from PIL import Image
import wave

# --- Utility Functions ---

# Marker to signal the end of the hidden message
MESSAGE_DELIMITER = "#####END#####" 

def text_to_binary(text):
    """Converts a string of text to a binary string."""
    # Prepend the delimiter to the message
    full_message = text + MESSAGE_DELIMITER
    # Convert each character to its 8-bit binary representation
    binary_data = ''.join(format(ord(char), '08b') for char in full_message)
    return binary_data

def binary_to_text(binary_data):
    """Converts a binary string back to text, stopping at the delimiter."""
    chars = []
    # Process 8 bits at a time (one character)
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        if len(byte) < 8:
            break
        char = chr(int(byte, 2))
        chars.append(char)
        
        # Check for the delimiter
        if "".join(chars).endswith(MESSAGE_DELIMITER):
            return "".join(chars).replace(MESSAGE_DELIMITER, "")
            
    return "".join(chars).replace(MESSAGE_DELIMITER, "") # Should stop before this with delimiter

def get_binary_data(file_path, mode):
    """Handles getting binary data from the cover file for decoding."""
    if mode == 'image':
        try:
            img = Image.open(file_path).convert('RGB')
            # Extract all LSBs from the R, G, B channels
            binary_data = ""
            for x in range(img.width):
                for y in range(img.height):
                    r, g, b = img.getpixel((x, y))
                    # Extract the LSB (last bit) of each color component
                    binary_data += bin(r)[-1]
                    binary_data += bin(g)[-1]
                    binary_data += bin(b)[-1]
            return binary_data
        except FileNotFoundError:
            print(f"Error: Image file not found at {file_path}")
            return None
        except Exception as e:
            print(f"An error occurred during image decoding: {e}")
            return None
            
    elif mode == 'audio':
        try:
            with wave.open(file_path, 'rb') as audio:
                frames = bytearray(audio.readframes(audio.getnframes()))
                # Extract the LSB of each byte
                binary_data = "".join([bin(byte)[-1] for byte in frames])
                return binary_data
        except FileNotFoundError:
            print(f"Error: Audio file not found at {file_path}")
            return None
        except wave.Error:
            print("Error: Invalid or non-WAV audio file format.")
            return None
        except Exception as e:
            print(f"An error occurred during audio decoding: {e}")
            return None
            
    return None

# --- Image Steganography ---

def encode_image():
    """Hides text in an image file (PNG recommended for LSB)."""
    print("\n--- Image Steganography: ENCODE ---")
    image_path = input("Enter the path to the cover image (e.g., 'cover.png'): ")
    secret_text = input("Enter the secret message to hide: ")
    output_path = input("Enter the output file name (e.g., 'stego_image.png'): ")

    try:
        img = Image.open(image_path).convert('RGB')
        binary_message = text_to_binary(secret_text)
        
        # Check capacity
        max_capacity = img.width * img.height * 3 # 3 bits per pixel (R, G, B)
        if len(binary_message) > max_capacity:
            print(f"\nError: Message is too long ({len(binary_message)} bits). Max capacity is {max_capacity} bits.")
            return

        data_index = 0
        new_img = img.copy()
        
        # Iterate over all pixels
        for x in range(new_img.width):
            for y in range(new_img.height):
                r, g, b = new_img.getpixel((x, y))
                pixels = [r, g, b]
                new_pixels = []

                for color_val in pixels:
                    if data_index < len(binary_message):
                        # Get the bit to embed (0 or 1)
                        message_bit = int(binary_message[data_index])
                        
                        # Clear the LSB (color_val & ~1) and set it to the message bit (color_val | message_bit)
                        new_color_val = (color_val & ~1) | message_bit
                        new_pixels.append(new_color_val)
                        data_index += 1
                    else:
                        new_pixels.append(color_val) # No more message, keep original pixel value
                
                new_img.putpixel((x, y), tuple(new_pixels))
                
                if data_index >= len(binary_message):
                    break
            if data_index >= len(binary_message):
                break

        # PNG is recommended as it's a lossless format, preserving the LSB changes.
        new_img.save(output_path) 
        print(f"\nSUCCESS: Message encoded and saved to '{output_path}'.")

    except FileNotFoundError:
        print(f"\nError: File not found at {image_path}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

def decode_image():
    """Extracts text from an image file."""
    print("\n--- Image Steganography: DECODE ---")
    image_path = input("Enter the path to the encoded image: ")
    
    binary_data = get_binary_data(image_path, 'image')
    if binary_data is None:
        return
        
    hidden_message = binary_to_text(binary_data)
    
    if hidden_message:
        print(f"\nSUCCESS: Hidden message decoded.")
        print("-" * 30)
        print(f"Message: {hidden_message}")
        print("-" * 30)
    else:
        print("\nCould not find a hidden message or the file is not a stego file.")

# --- Audio Steganography ---
def encode_audio():
    """Hides text in a WAV audio file."""
    print("\n--- Audio Steganography: ENCODE ---")
    audio_path = input("Enter the path to the cover audio file (must be WAV): ")
    secret_text = input("Enter the secret message to hide: ")
    output_path = input("Enter the output file name (e.g., 'stego_audio.wav'): ")

    try:
        with wave.open(audio_path, 'rb') as audio:
            # Read parameters and all frame bytes
            params = audio.getparams()
            frames = bytearray(audio.readframes(audio.getnframes()))
            
        binary_message = text_to_binary(secret_text)
        
        # Check capacity: 1 bit per byte
        max_capacity = len(frames) 
        if len(binary_message) > max_capacity:
            print(f"\nError: Message is too long ({len(binary_message)} bits). Max capacity is {max_capacity} bits.")
            return

        # Embed the binary message into the LSB of each frame byte
        for i in range(len(binary_message)):
            message_bit = int(binary_message[i])
            
            # Clear the LSB (frames[i] & ~1) and set it to the message bit
            frames[i] = (frames[i] & 254) | message_bit # 254 is ~1 in 8-bit
            
        # Write the modified frames to a new WAV file
        with wave.open(output_path, 'wb') as new_audio:
            new_audio.setparams(params)
            new_audio.writeframes(frames)
            
        print(f"\nSUCCESS: Message encoded and saved to '{output_path}'.")

    except FileNotFoundError:
        print(f"\nError: File not found at {audio_path}")
    except wave.Error:
        print("\nError: Invalid or non-WAV audio file format. This tool only supports WAV.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

def decode_audio():
    """Extracts text from an audio file."""
    print("\n--- Audio Steganography: DECODE ---")
    audio_path = input("Enter the path to the encoded audio (WAV) file: ")
    
    binary_data = get_binary_data(audio_path, 'audio')
    if binary_data is None:
        return

    hidden_message = binary_to_text(binary_data)

    if hidden_message:
        print(f"\nSUCCESS: Hidden message decoded.")
        print("-" * 30)
        print(f"Message: {hidden_message}")
        print("-" * 30)
    else:
        print("\nCould not find a hidden message or the file is not a stego file.")

# --- Video Steganography (Conceptual Placeholder) ---

def handle_video_steganography():
    """
    Conceptual function for Video Steganography.
    (Requires external libraries and is more complex.)
    """
    print("\n--- Video Steganography ---")
    print("Video steganography is significantly more complex, especially with compressed formats like MP4.")
    print("This basic tool does not implement full video steganography.")
    print("Please use the Image or Audio options for a complete demonstration.")

# --- Main Menu and Controller ---

def main():
    """Main menu-driven controller for the steganography tool."""
    while True:
        print("\n" + "="*40)
        print("    PYTHON STEGANOGRAPHY TOOL MENU")
        print("="*40)
        print("1: Image Steganography (LSB)")
        print("2: Audio Steganography (LSB - WAV only)")
        print("3: Video Steganography (Conceptual)")
        print("4: Exit")
        print("-" * 40)
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            print("\n--- Image Steganography Options ---")
            sub_choice = input("Enter (E) to Encode or (D) to Decode: ").strip().upper()
            if sub_choice == 'E':
                encode_image()
            elif sub_choice == 'D':
                decode_image()
            else:
                print("Invalid sub-option.")
                
        elif choice == '2':
            print("\n--- Audio Steganography Options ---")
            sub_choice = input("Enter (E) to Encode or (D) to Decode: ").strip().upper()
            if sub_choice == 'E':
                encode_audio()
            elif sub_choice == 'D':
                decode_audio()
            else:
                print("Invalid sub-option.")
                
        elif choice == '3':
            handle_video_steganography()
            
        elif choice == '4':
            print("Exiting Steganography Tool. Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()