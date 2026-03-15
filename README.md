# Ijtimai Qurbani Management System

A comprehensive Python-based application for managing collective Qurbani operations in mosques.

## Features

- **Participant Management**: Add, edit, delete participants with details like name, phone, address, CNIC.
- **Animal Management**: Record animals with type, purchase price, seller details, and total shares.
- **Share Allocation**: Allocate shares to participants, preventing over-allocation.
- **Payment Tracking**: Record payments, track balances, and view payment history.
- **Receipt Generation**: Generate professional PDF receipts and print them.
- **Reports and Analytics**: View statistics and export to Excel.
- **Search and Filter**: Search participants by name or phone.
- **Meat Distribution**: Mark participants as meat delivered.
- **Backup and Restore**: Backup and restore database files.
- **Admin Login**: Secure access with username and password.

## Requirements

- Python 3.7+
- Tkinter (usually included with Python)
- fpdf
- openpyxl

## Installation

1. Clone or download the project.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`

## Usage

1. Login with default credentials: username `admin`, password `admin123`
2. Use the dashboard to manage participants, animals, payments.
3. Generate reports and export data.

## Database

The application uses SQLite database (`qurbani.db`) for data storage.

## Modules

- `main.py`: Entry point
- `database.py`: Database operations
- `pdf_generator.py`: PDF receipt generation
- `gui/`: GUI components
  - `login_window.py`: Login screen
  - `main_window.py`: Main application window
  - `participant_form.py`: Participant add/edit form
  - `animal_form.py`: Animal add form
  - `payment_form.py`: Payment record form
  - `report_window.py`: Reports window

## License

This project is open-source. Use at your own risk.