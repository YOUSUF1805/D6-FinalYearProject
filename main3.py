from tkinter import Tk, Frame, Button, Label, filedialog, Toplevel, Canvas
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from mini4_1 import encode_images_multiple, decode_images_multiple


class SteganographyApp:
    """
    A GUI-based application for performing image steganography operations.
    Allows users to encode hidden images into carrier images and decode them later.

    Features:
    - Encoding multiple images into carrier images.
    - Decoding hidden images from encoded carrier images.
    - Dynamic and responsive GUI.
    - Background image resizing support.
    """

    def __init__(self, root):
        """
        Initialize the main application window and setup the GUI components.

        Args:
            root (Tk): The main Tkinter root window.
        """
        self.root = root
        self.root.title("Image Steganography")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Set background image
        self.bg_image = None
        self.set_background_image("background.png")  # Replace with the path to your background image

        self.show_main_menu()

    def set_background_image(self, image_path):
        """
        Sets a background image for the main application window.

        Args:
            image_path (str): The file path of the background image.
        """
        try:
            bg = Image.open(image_path)
            self.bg_image = ImageTk.PhotoImage(bg)
            canvas = Canvas(self.root, width=bg.width, height=bg.height)
            canvas.pack(fill="both", expand=True)
            canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
            self.canvas = canvas
        except FileNotFoundError:
            print(f"Background image {image_path} not found.")
            self.canvas = None

    def show_main_menu(self):
        """
        Displays the main menu of the application with options for encoding, decoding, and exiting.
        """
        self.clear_screen()

        Label(self.root, text="Image Steganography", font=("Helvetica", 20), bg="lightblue").pack(pady=20)

        Button(self.root, text="Encode Images", command=self.show_encode_menu, font=("Helvetica", 14), bg="green",
               fg="white").pack(pady=10)
        Button(self.root, text="Decode Images", command=self.show_decode_menu, font=("Helvetica", 14), bg="blue",
               fg="white").pack(pady=10)
        Button(self.root, text="Exit", command=self.root.quit, font=("Helvetica", 14), bg="red", fg="white").pack(
            pady=10)

    def show_encode_menu(self):
        """
        Displays the encoding interface where users can select carrier and hidden images to encode.
        """
        self.clear_screen()

        Label(self.root, text="Encode Images", font=("Helvetica", 18), bg="lightblue").pack(pady=20)

        Button(self.root, text="Select Carrier Images", command=self.select_carrier_images, font=("Helvetica", 14),
               bg="green", fg="white").pack(pady=10)
        Button(self.root, text="Select Hidden Images", command=self.select_hidden_images, font=("Helvetica", 14),
               bg="blue", fg="white").pack(pady=10)
        Button(self.root, text="Encode", command=self.encode_images, font=("Helvetica", 14), bg="purple",
               fg="white").pack(pady=10)
        Button(self.root, text="Back", command=self.show_main_menu, font=("Helvetica", 14), bg="red", fg="white").pack(
            pady=10)

        self.carrier_images = []
        self.hidden_images = []

    def show_decode_menu(self):
        """
        Displays the decoding interface where users can select encoded images to decode hidden data.
        """
        self.clear_screen()

        Label(self.root, text="Decode Images", font=("Helvetica", 18), bg="lightblue").pack(pady=20)

        Button(self.root, text="Select Encoded Images", command=self.select_encoded_images, font=("Helvetica", 14),
               bg="green", fg="white").pack(pady=10)
        Button(self.root, text="Decode", command=self.decode_images, font=("Helvetica", 14), bg="purple",
               fg="white").pack(pady=10)
        Button(self.root, text="Back", command=self.show_main_menu, font=("Helvetica", 14), bg="red", fg="white").pack(
            pady=10)

        self.encoded_images = []

    def select_carrier_images(self):
        """
        Allows the user to select carrier images via a file dialog.
        """
        self.carrier_images = filedialog.askopenfilenames(title="Select Carrier Images",
                                                          filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        print("Carrier Images Selected:", self.carrier_images)

    def select_hidden_images(self):
        """
        Allows the user to select hidden images via a file dialog.
        """
        self.hidden_images = filedialog.askopenfilenames(title="Select Hidden Images",
                                                         filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        print("Hidden Images Selected:", self.hidden_images)

    def encode_images(self):
        """
        Encodes hidden images into the selected carrier images.
        """
        if not self.carrier_images or not self.hidden_images:
            messagebox.showerror("Error", "Please select both carrier and hidden images.")
            return

        try:
            carrier_paths = self.carrier_images
            hidden_imgs = [Image.open(path).convert("RGB") for path in self.hidden_images]

            encoded_imgs = encode_images_multiple(carrier_paths, hidden_imgs)
            for idx, encoded_img in enumerate(encoded_imgs):
                save_path = f"encoded_image_{idx + 1}.png"
                encoded_img.save(save_path)
                print(f"Encoded image saved as {save_path}")
                messagebox.showinfo("Success", f"Encoded image saved as {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error during encoding: {e}")

    def select_encoded_images(self):
        """
        Allows the user to select encoded images via a file dialog.
        """
        self.encoded_images = filedialog.askopenfilenames(title="Select Encoded Images",
                                                          filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        print("Encoded Images Selected:", self.encoded_images)

    def decode_images(self):
        """
        Decodes hidden images from the selected encoded images.
        """
        if not self.encoded_images:
            messagebox.showerror("Error", "Please select encoded images.")
            return

        try:
            decoded_images = decode_images_multiple(self.encoded_images)
            for idx, img in enumerate(decoded_images):
                save_path = f"decoded_hidden_image_{idx + 1}.png"
                img.save(save_path)
                print(f"Decoded hidden image saved as {save_path}")
                messagebox.showinfo("Success", f"Decoded hidden image saved as {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error during decoding: {e}")

    def clear_screen(self):
        """
        Clears the current screen by destroying all child widgets.
        """
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = Tk()
    app = SteganographyApp(root)
    root.mainloop()
