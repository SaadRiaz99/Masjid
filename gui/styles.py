from tkinter import ttk
import tkinter as tk

class StyleManager:
    LIGHT_THEME = {
        "primary": "#2c3e50",
        "secondary": "#27ae60",
        "accent": "#3498db",
        "danger": "#e74c3c",
        "background": "#f4f7f6",
        "card": "#ffffff",
        "text_main": "#2c3e50",
        "text_light": "#7f8c8d",
        "tree_bg": "#ffffff",
        "tree_heading": "#dcdde1"
    }
    
    DARK_THEME = {
        "primary": "#ecf0f1",
        "secondary": "#2ecc71",
        "accent": "#3498db",
        "danger": "#e74c3c",
        "background": "#2c3e50",
        "card": "#34495e",
        "text_main": "#ecf0f1",
        "text_light": "#bdc3c7",
        "tree_bg": "#34495e",
        "tree_heading": "#2c3e50"
    }

    @staticmethod
    def apply_styles(root, dark_mode=False):
        theme = StyleManager.DARK_THEME if dark_mode else StyleManager.LIGHT_THEME
        style = ttk.Style()
        style.theme_use('clam')

        root.configure(bg=theme["background"])

        # General configuration
        style.configure(".", font=('Segoe UI', 10), background=theme["background"], foreground=theme["text_main"])

        # Notebook (Tabs)
        style.configure("TNotebook", background=theme["background"], borderwidth=0)
        style.configure("TNotebook.Tab", 
                        padding=[15, 8], 
                        font=('Segoe UI', 10, 'bold'),
                        background=theme["tree_heading"],
                        foreground=theme["text_main"])
        style.map("TNotebook.Tab", 
                  background=[("selected", theme["secondary"])], 
                  foreground=[("selected", "#ffffff")])

        # Treeview
        style.configure("Treeview", 
                        background=theme["tree_bg"],
                        fieldbackground=theme["tree_bg"],
                        foreground=theme["text_main"],
                        rowheight=30,
                        font=('Segoe UI', 10),
                        borderwidth=0)
        style.configure("Treeview.Heading", 
                        background=theme["tree_heading"], 
                        foreground=theme["text_main"], 
                        font=('Segoe UI', 10, 'bold'),
                        relief="flat")
        style.map("Treeview", background=[('selected', theme["accent"])], foreground=[('selected', "#ffffff")])

        # Buttons
        style.configure("TButton", 
                        font=('Segoe UI', 10, 'bold'), 
                        padding=[12, 6],
                        background=theme["accent"],
                        foreground="#ffffff",
                        borderwidth=0)
        style.map("TButton", 
                  background=[('active', '#2980b9'), ('disabled', '#bdc3c7')],
                  foreground=[('active', "#ffffff")])

        style.configure("Success.TButton", background=theme["secondary"], foreground="#ffffff")
        style.map("Success.TButton", background=[('active', '#219150')])

        style.configure("Danger.TButton", background=theme["danger"], foreground="#ffffff")
        style.map("Danger.TButton", background=[('active', '#c0392b')])

        # Frames
        style.configure("TFrame", background=theme["background"])
        style.configure("Card.TFrame", background=theme["card"], relief="flat", borderwidth=0)
        
        # Labelframes
        style.configure("TLabelframe", background=theme["background"], borderwidth=1, relief="solid")
        style.configure("TLabelframe.Label", background=theme["background"], foreground=theme["primary"], font=('Segoe UI', 10, 'bold'))

        # Labels
        style.configure("TLabel", background=theme["background"], foreground=theme["text_main"])
        style.configure("Header.TLabel", font=('Segoe UI', 20, 'bold'), foreground=theme["primary"], background=theme["background"])
        style.configure("SubHeader.TLabel", font=('Segoe UI', 13, 'bold'), foreground=theme["secondary"], background=theme["background"])
        style.configure("Footer.TLabel", font=('Segoe UI', 9), foreground=theme["text_light"], background=theme["background"])
        
        # Entry
        style.configure("TEntry", fieldbackground=theme["card"], padding=5)

        return style

def apply_styles(root):
    # Default wrapper for backward compatibility
    return StyleManager.apply_styles(root)