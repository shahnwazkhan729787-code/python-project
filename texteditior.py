import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.title("Text Editor")
root.geometry("600x400")

text = tk.Text(root, bg="#1e1e2f", fg="white", font=("Arial", 12))
text.pack(fill="both", expand=True)

def open_file():
    file = filedialog.askopenfile()
    if file:
        text.delete("1.0", tk.END)
        text.insert(tk.END, file.read())

def save_file():
    file = filedialog.asksaveasfile(mode='w')
    if file:
        file.write(text.get("1.0", tk.END))

menu = tk.Menu(root)
root.config(menu=menu)

file_menu = tk.Menu(menu)
menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)

root.mainloop()