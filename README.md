# 📚 Homework Tracker

> A clean desktop application for tutors to monitor and manage students' homework assignments.

Built with **Python** and **CustomTkinter**, with persistent JSON storage — no database setup required.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-informational)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

| Feature | Details |
|---|---|
| **Add / remove students** | Manage your student roster from the sidebar |
| **Add assignments** | Set a title, optional notes, and an assigned date |
| **Delete assignments** | Remove a task with a confirmation prompt |
| **Toggle status** | Mark assignments as *Done* or revert to *Pending* |
| **Student history** | Full assignment log per student with dates and statuses |
| **Completion stats** | Live count and percentage shown in the student header |
| **Filter by status** | View All / Pending / Done assignments instantly |
| **Search students** | Real-time name filtering in the sidebar |
| **Persistent storage** | All data saved automatically to `homework_data.json` |

---

## 🚀 Getting Started

### Prerequisites

- Python **3.10** or newer

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/homework-tracker.git
   cd homework-tracker
   ```

2. **Install the only required dependency**
   ```bash
   pip install customtkinter
   ```

3. **Run the app**
   ```bash
   python main.py
   ```

That's it — no virtual environment or additional configuration needed.

---

## 📁 Project Structure

```
homework-tracker/
├── main.py              # Entry point — run this file
├── data_manager.py      # Business logic & JSON persistence (no UI code)
├── app.py               # CustomTkinter GUI (no business logic)
├── homework_data.json   # Auto-generated database (git-ignored)
├── .gitignore
└── README.md
```

### Architecture

The project follows a strict **separation of concerns**:

```
main.py
  │
  ├── DataManager (data_manager.py)
  │     Pure Python — reads/writes homework_data.json
  │     Raises domain exceptions (StudentNotFound, AssignmentNotFound, …)
  │
  └── HomeworkTrackerApp (app.py)
        CustomTkinter root window
        ├── StudentPanel          — left sidebar
        │     AddStudentDialog    — modal
        ├── StudentDetailPanel    — main content area
        │     AddAssignmentDialog — modal
        └── AssignmentRow         — individual task widget
```

---

## 🛡️ Error Handling

- **Empty student name** → error dialog, no data written
- **Empty assignment title** → error dialog, no data written
- **Invalid date format** → error dialog with format hint
- **Deleting a student or assignment** always requires confirmation
- **Corrupted JSON file** → app starts with an empty database and logs a warning to the console

---

## 🗂️ Data Format

Data is stored in plain JSON (`homework_data.json`):

```json
{
  "students": {
    "<uuid>": {
      "id": "...",
      "full_name": "Alice Johnson",
      "date_added": "2024-10-28",
      "assignments": {
        "<uuid>": {
          "id": "...",
          "title": "Algebra exercises p.45",
          "description": "Exercises 1 through 10",
          "date_assigned": "2024-10-28",
          "status": "Done"
        }
      }
    }
  }
}
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| [customtkinter](https://github.com/TomSchimansky/CustomTkinter) | ≥ 6.0 | Modern Tkinter UI widgets |
| `tkinter` | stdlib | Base GUI framework |

All other imports (`json`, `uuid`, `pathlib`, `datetime`) are part of the Python standard library.
