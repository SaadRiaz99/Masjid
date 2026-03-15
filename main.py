import tkinter as tk
from gui.login_window import LoginWindow
from gui.main_window import MainWindow

def main():
    root = tk.Tk()
    root.withdraw()  # Hide main window initially

    def on_login_success():
        MainWindow(tk.Tk())

    LoginWindow(root, on_login_success)
    root.mainloop()

if __name__ == "__main__":
    main()