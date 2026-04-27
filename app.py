import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO

ACCESS_KEY = "r7h1WKJT05wJpoig06BFA9R-PZcLcYE6LyBtCfLfF2U"

root = tk.Tk()
root.title("Image Gallery")
root.geometry("700x600")
root.configure(bg="#0f172a")

# Title
tk.Label(root, text="Image Gallery",
         font=("Segoe UI", 20, "bold"),
         bg="#0f172a", fg="white").pack(pady=10)

# Search box
entry = tk.Entry(root, font=("Segoe UI", 12),
                 bg="#1e293b", fg="white", bd=0)
entry.pack(padx=20, pady=10, fill="x", ipady=8)

# Frame for images
img_frame = tk.Frame(root, bg="#0f172a")
img_frame.pack(pady=10)

image_labels = []

# Create placeholders (2 rows × 3 columns)
for i in range(2):
    for j in range(3):
        frame = tk.Frame(img_frame, bg="#1e293b", bd=2, relief="ridge")
        frame.grid(row=i, column=j, padx=10, pady=10)

        lbl = tk.Label(frame, bg="#1e293b")
        lbl.pack()
        image_labels.append(lbl)

def fetch_images():
    query = entry.get()

    for i in range(6):
        try:
            url = f"https://api.unsplash.com/photos/random?query={query}&client_id={ACCESS_KEY}"
            response = requests.get(url).json()

            img_url = response['urls']['small']
            img_data = requests.get(img_url).content

            img = Image.open(BytesIO(img_data))
            img = img.resize((180, 120))

            img_tk = ImageTk.PhotoImage(img)

            image_labels[i].config(image=img_tk)
            image_labels[i].image = img_tk

        except:
            print("Error loading image")

# Button
tk.Button(root, text="Search Images",
          bg="#3b82f6", fg="white",
          font=("Segoe UI", 12),
          bd=0, command=fetch_images).pack(pady=10)

root.mainloop()