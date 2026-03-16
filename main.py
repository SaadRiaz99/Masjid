import tkinter as tk
from gui.login_window import LoginWindow
from gui.main_window import MainWindow
from gui.styles import apply_styles

def main():
    root = tk.Tk()
    root.title("Qurbani Management System")
    
    # Apply global styles
    apply_styles(root)

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