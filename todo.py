import tkinter as tk

root = tk.Tk()
root.title("To-Do List")
root.geometry("300x400")
root.configure(bg="#2c2c3c")

def add():
    listbox.insert(tk.END, entry.get())
    entry.delete(0, tk.END)

def delete():
    listbox.delete(tk.ANCHOR)

entry = tk.Entry(root, font=("Arial", 12))
entry.pack(pady=10, padx=10, fill="x")

tk.Button(root, text="Add Task", bg="#28a745", fg="white",
          command=add).pack(pady=5)

tk.Button(root, text="Delete Task", bg="#dc3545", fg="white",
          command=delete).pack(pady=5)

listbox = tk.Listbox(root, font=("Arial", 12))
listbox.pack(padx=10, pady=10, fill="both", expand=True)

root.mainloop()