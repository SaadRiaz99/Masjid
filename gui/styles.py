from tkinter import ttk

def apply_styles(root):
    style = ttk.Style()
    style.theme_use('clam')  # Use 'clam' as base for better customization

    # Colors
    primary = "#4CAF50"     # Green
    secondary = "#FF9800"   # Orange
    accent = "#2196F3"      # Blue
    background = "#F5F5F5"
    text_color = "#333333"
    white = "#FFFFFF"
    
    # Configure root background
    root.configure(bg=background)

    # Tabs
    style.configure("TNotebook", background=background)
    style.configure("TNotebook.Tab", padding=[10, 5], font=('Segoe UI', 10, 'bold'))
    style.map("TNotebook.Tab", background=[("selected", primary)], foreground=[("selected", white)])

    # Treeview
    style.configure("Treeview", 
                    background=white,
                    fieldbackground=white,
                    foreground=text_color,
                    rowheight=25,
                    font=('Segoe UI', 10))
    style.configure("Treeview.Heading", 
                    background=primary, 
                    foreground=white, 
                    font=('Segoe UI', 11, 'bold'))
    style.map("Treeview", background=[('selected', accent)])

    # Buttons
    style.configure("TButton", 
                    font=('Segoe UI', 10), 
                    padding=6,
                    background=primary,
                    foreground=white)
    style.map("TButton", 
              background=[('active', '#45a049')],  # Darker green on hover
              foreground=[('active', white)])

    # Frames
    style.configure("TFrame", background=background)
    style.configure("Card.TFrame", background=white, relief="raised", borderwidth=1)

    # Labels
    style.configure("TLabel", background=background, foreground=text_color, font=('Segoe UI', 10))
    style.configure("Header.TLabel", font=('Segoe UI', 16, 'bold'), foreground=primary)
    style.configure("SubHeader.TLabel", font=('Segoe UI', 12, 'bold'), foreground=secondary)
    
    # Custom Danger Button
    style.configure("Danger.TButton", background="#f44336", foreground=white)
    style.map("Danger.TButton", background=[('active', '#d32f2f')])

    return style