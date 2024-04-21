import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Label, Frame, Style  # Styles for color management
from PIL import Image, ImageTk
import image_proc as ip
import pytesseract
import logging
from tkinterdnd2 import TkinterDnD, DND_FILES

logging.basicConfig(level=logging.ERROR)

root = TkinterDnD.Tk()
root.title("OCR test")

root.geometry("800x600")  # Default window size

background_color = "#333333"
root.configure(background=background_color)

style = Style()
style.theme_use("clam")
style.configure("TFrame", background=background_color)
style.configure("TLabel", background=background_color, foreground="#FFFFFF")

left_frame = Frame(root, style="TFrame")
center_frame = Frame(root, style="TFrame")
right_frame = Frame(root, style="TFrame")

left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

left_label_text = "Przeciągnij plik\ngraficzny tutaj"
left_label = Label(left_frame, text=left_label_text, style="TLabel", borderwidth=1, relief="solid")
left_label.pack(fill=tk.BOTH, expand=True)

center_image_label = Label(center_frame, style="TLabel")
center_image_label.pack(fill=tk.BOTH, expand=True)

right_text_label = Label(right_frame, style="TLabel", text="Wyodrębniony tekst będzie tutaj")
right_text_label.pack(fill=tk.BOTH, expand=True)

def on_drop(event):
    file_name = event.data.strip('{}')
    process_image(file_name)

def process_image(file_name):
    blurred, original, resize_ratio = ip.prepare_image(file_name)
    try:
        restored, restored_contrast = ip.perspective_restoration(blurred, original, resize_ratio)
    except Exception as e:
        logging.error(f"Nie można przywrócić perspektywy: {e}")
        messagebox.showerror("Błąd", "Nie można przywrócić perspektywy")
        restored_contrast = blurred

    processed_image = ip.preprocess_image(restored_contrast)

    display_image = Image.fromarray(processed_image)
    display_image = display_image.resize((280, 500))
    image_tk = ImageTk.PhotoImage(display_image)
    center_image_label.config(image=image_tk)
    center_image_label.image = image_tk

    extracted_text = pytesseract.image_to_string(processed_image, config="--oem 3 --psm 4")
    right_text_label.config(text=extracted_text)

root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

root.mainloop()