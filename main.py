import tkinter as tk
from tkinter import messagebox
from data_manager import DatabaseError, DataManager
from app import HomeworkTrackerApp


def main() -> None:
    try:
        dm = DataManager()
    except DatabaseError as exc:
        root = tk.Tk()
        root.withdraw()
        try:
            messagebox.showerror('Database error', str(exc), parent=root)
        finally:
            root.destroy()
        return
    app = HomeworkTrackerApp(dm)
    app.mainloop()


if __name__ == '__main__':
    main()
