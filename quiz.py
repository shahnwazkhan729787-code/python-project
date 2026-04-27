import tkinter as tk

root = tk.Tk()
root.title("Quiz App")
root.geometry("400x300")
root.configure(bg="#0f172a")

questions = [
    ("Python is?", ["Language", "Car"], 0),
    ("2 + 2 = ?", ["3", "4"], 1),
    ("HTML is?", ["Programming", "Markup"], 1)
]

index = 0
score = 0

def check(ans):
    global index, score
    if ans == questions[index][2]:
        score += 1
    index += 1
    load_question()

def load_question():
    if index < len(questions):
        q_label.config(text=questions[index][0])
        b1.config(text=questions[index][1][0],
                  command=lambda: check(0))
        b2.config(text=questions[index][1][1],
                  command=lambda: check(1))
    else:
        q_label.config(text=f"🎉 Your Score: {score}/{len(questions)}")
        b1.pack_forget()
        b2.pack_forget()

# Title
title = tk.Label(root, text="Quiz App",
                 font=("Segoe UI", 18, "bold"),
                 bg="#0f172a", fg="white")
title.pack(pady=10)

# Question
q_label = tk.Label(root, text="",
                   font=("Segoe UI", 14),
                   bg="#1e293b", fg="white",
                   wraplength=300, padx=10, pady=10)
q_label.pack(pady=20)

# Buttons
b1 = tk.Button(root, width=20, height=2,
               bg="#3b82f6", fg="white",
               bd=0, font=("Segoe UI", 11))
b1.pack(pady=5)

b2 = tk.Button(root, width=20, height=2,
               bg="#10b981", fg="white",
               bd=0, font=("Segoe UI", 11))
b2.pack(pady=5)

load_question()
root.mainloop()