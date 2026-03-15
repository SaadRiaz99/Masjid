import tkinter as tk
from gui.login_window import LoginWindow
from gui.main_window import MainWindow

def main():
    root = tk.Tk()
    root.title("Qurbani Management System")

    def on_login_success():
        # Hide the login window or clear the root
        for widget in root.winfo_children():
            widget.destroy()
        
        # Open the main window on the same root
        MainWindow(root)

    LoginWindow(root, on_login_success)
    root.mainloop()

if __name__ == "__main__":
    main()