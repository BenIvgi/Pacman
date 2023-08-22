import tkinter as tk

offset = 15


def encrypt(msg):
    return "".join([chr(ord(let) + offset) for let in msg][::-1])


def decrypt(msg):
    return "".join([chr(ord(let) - offset) for let in msg][::-1])


def key_window(func):

    def check_password():
        func(entry.get() or "default_password")
        window.destroy()


    # Create the main window
    window = tk.Tk()
    window.iconbitmap("icon.ico")
    window.title("Enter Password (Gatekeeping Services)")

    # Set window size
    window.geometry("300x100")
    window.geometry("+600+200")

    # Create label
    label_text = "Please enter Game Key:"
    label = tk.Label(window, text=label_text)
    label.pack()

    # Create entry (textbox)
    entry = tk.Entry(window)
    entry.pack()

    # Create button
    button = tk.Button(window, text="Connect", command=check_password)
    button.pack()

    window.mainloop()
