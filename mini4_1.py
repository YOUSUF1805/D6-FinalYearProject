from PIL import Image
import numpy as np

# Convert pixel data to binary
def genData(data):
    return [format(value, '08b') for value in data]

# Modify pixels to embed binary data
def modPix(pix, data):
    datalist = genData(data)
    lendata = len(datalist)
    imdata = iter(pix)

    for i in range(lendata):
        pix = [value for value in imdata.__next__()[:3] +
               imdata.__next__()[:3] +
               imdata.__next__()[:3]]

        # Modify pixel values to embed data
        for j in range(8):
            if datalist[i][j] == '0' and pix[j] % 2 != 0:
                pix[j] -= 1
            elif datalist[i][j] == '1' and pix[j] % 2 == 0:
                pix[j] = pix[j] - 1 if pix[j] != 0 else pix[j] + 1

        # Stop marker
        if i == lendata - 1:
            if pix[-1] % 2 == 0:
                pix[-1] = pix[-1] - 1 if pix[-1] != 0 else pix[-1] + 1
        else:
            if pix[-1] % 2 != 0:
                pix[-1] -= 1

        pix = tuple(pix)
        yield pix[:3]
        yield pix[3:6]
        yield pix[6:9]

# Encode multiple hidden images into a carrier image
def encode_images_multiple(carrier_img_paths, hidden_imgs):
    # Prepare hidden data
    hidden_data = b""
    for idx, hidden_img in enumerate(hidden_imgs):
        hidden_pixels = list(hidden_img.getdata())
        hidden_width, hidden_height = hidden_img.size
        metadata = f"{hidden_width}x{hidden_height}$$IMG{idx}$$".encode()
        image_data = metadata + bytes([val for pixel in hidden_pixels for val in pixel])
        hidden_data += image_data

    hidden_data += b"$$END$$"  # Append stop marker

    # Debugging: Print hidden data size
    print(f"Total Hidden Data Size (bytes): {len(hidden_data)}")

    carrier_imgs = [Image.open(path).convert("RGB") for path in carrier_img_paths]
    encoded_imgs = []

    for carrier_img in carrier_imgs:
        # Calculate the carrier's capacity
        carrier_capacity_bits = carrier_img.size[0] * carrier_img.size[1] * 3
        chunk_size = carrier_capacity_bits // 8  # Convert capacity from bits to bytes

        if len(hidden_data) > chunk_size:
            # Take the chunk that fits into this carrier image
            data_chunk, hidden_data = hidden_data[:chunk_size], hidden_data[chunk_size:]
        else:
            data_chunk, hidden_data = hidden_data, b""

        # Debugging: Print chunk size
        print(f"Data Chunk Size for Carrier Image (bytes): {len(data_chunk)}")

        # Encode the chunk into the carrier image
        mod_pixel_generator = modPix(carrier_img.getdata(), data_chunk)
        new_img = carrier_img.copy()
        (x, y) = (0, 0)
        try:
            for pixel in mod_pixel_generator:
                new_img.putpixel((x, y), pixel)
                x = (x + 1) % carrier_img.size[0]
                y += (x == 0)  # Move to next row if at the end of the current row
        except StopIteration:
            print("StopIteration occurred. Ensure the chunk size matches carrier capacity.")
            break

        encoded_imgs.append(new_img)

        # If all data is encoded, stop
        if not hidden_data:
            break

    if hidden_data:
        raise ValueError("Not enough carrier images to encode all hidden data.")

    return encoded_imgs


def calculate_mse(original_image, encoded_image):
    original = np.array(original_image)
    encoded = np.array(encoded_image)
    mse = np.mean((original - encoded) ** 2)
    return mse

def calculate_psnr(original_image, encoded_image):
    mse = calculate_mse(original_image, encoded_image)
    if mse == 0:
        return float('inf')  # If MSE is zero, PSNR is infinite (images are identical)
    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return psnr


# Decode multiple hidden images from a carrier image
# Extract metadata and reconstruct images
def decode_images_multiple(encoded_img_paths):
    binary_data = ""

    for path in encoded_img_paths:
        encoded_img = Image.open(path).convert("RGB")
        imgdata = iter(encoded_img.getdata())

        # Extract binary data from LSBs
        while True:
            try:
                pixels = [value for value in imgdata.__next__()[:3] +
                          imgdata.__next__()[:3] +
                          imgdata.__next__()[:3]]
            except StopIteration:
                break

            for i in pixels[:8]:
                binary_data += '0' if i % 2 == 0 else '1'

            # Stop marker
            if pixels[-1] % 2 != 0:
                break

    # Convert binary data to bytes
    byte_data = bytearray()
    for i in range(0, len(binary_data), 8):
        byte_data.append(int(binary_data[i:i + 8], 2))

    # Extract metadata and reconstruct images
    hidden_images = []
    while b"$$IMG" in byte_data:
        metadata_end_idx = byte_data.index(b"$$")
        metadata = byte_data[:metadata_end_idx].decode()
        hidden_width, hidden_height = map(int, metadata.split('x'))

        pixel_data_start_idx = metadata_end_idx + len(b"$$IMG0$$")
        pixel_data_end_idx = pixel_data_start_idx + (hidden_width * hidden_height * 3)

        pixel_data = byte_data[pixel_data_start_idx:pixel_data_end_idx]
        hidden_pixels = [tuple(pixel_data[i:i + 3]) for i in range(0, len(pixel_data), 3)]

        hidden_img = Image.new("RGB", (hidden_width, hidden_height))
        hidden_img.putdata(hidden_pixels)
        hidden_images.append(hidden_img)

        byte_data = byte_data[pixel_data_end_idx:]  # Move to the next image's data

    return hidden_images

def calculate_accuracy(original_hidden_image, decoded_hidden_image):
    original = np.array(original_hidden_image)
    decoded = np.array(decoded_hidden_image)
    matching_pixels = np.sum(original == decoded)
    total_pixels = original.size
    accuracy = (matching_pixels / total_pixels) * 100
    return accuracy


# Main function to handle encoding and decoding
def main():
    choice = int(input(":: Welcome to Image Steganography with LSB ::\n1. Encode\n2. Decode\nEnter your choice: "))
    if choice == 1:
        carrier_img_paths = input("Enter carrier image paths (comma-separated): ").split(",")
        num_hidden_images = int(input("Enter the number of hidden images: "))
        hidden_imgs = []

        for i in range(num_hidden_images):
            hidden_img_path = input(f"Enter hidden image {i + 1} name (with extension): ")
            hidden_img = Image.open(hidden_img_path).convert("RGB")
            hidden_img = hidden_img.resize((hidden_img.width // 2, hidden_img.height // 2), Image.LANCZOS)
            hidden_imgs.append(hidden_img)

        encoded_imgs = encode_images_multiple(carrier_img_paths, hidden_imgs)
        for idx, encoded_img in enumerate(encoded_imgs):
            encoded_img_name = f"encoded_image_{idx + 1}.png"
            encoded_img.save(encoded_img_name)
            print(f"Encoded image saved as {encoded_img_name}")
    elif choice == 2:
        encoded_img_paths = input("Enter encoded image paths (comma-separated): ").split(",")
        hidden_images = decode_images_multiple(encoded_img_paths)
        for idx, hidden_img in enumerate(hidden_images):
            hidden_img_name = input(f"Enter the name to save hidden image {idx + 1} (with extension): ")
            hidden_img.save(hidden_img_name)
            print(f"Hidden image {idx + 1} saved as {hidden_img_name}")
    else:
        print("Invalid choice. Please select 1 for Encode or 2 for Decode.")


# Driver code
if __name__ == "__main__":
    main()
