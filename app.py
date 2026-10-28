from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from datetime import date
from typing import Optional

import customtkinter as ctk

from data_manager import (
    DataManager,
    InvalidFieldValue,
    StudentNotFound,
    AssignmentNotFound,
    STATUS_DONE,
    STATUS_PENDING,
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLOR_DONE = "#2ecc71"
COLOR_PENDING = "#e74c3c"

class AddStudentDialog(ctk.CTkToplevel):

    def __init__(self, parent: ctk.CTk, on_submit):
        super().__init__(parent)
        self.title("Add Student")
        self.geometry("380x180")
        self.resizable(False, False)
        self.grab_set()

        self._on_submit = on_submit
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Student's full name:", anchor="w").grid(
            row=0, column=0, padx=20, pady=(20, 4), sticky="ew"
        )
        self._name_entry = ctk.CTkEntry(self, placeholder_text="e.g. Anna Smith")
        self._name_entry.grid(row=1, column=0, padx=20, pady=(0, 16), sticky="ew")
        self._name_entry.focus()

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_frame, text="Add", command=self._confirm).grid(
            row=0, column=0, padx=(0, 8), sticky="ew"
        )
        ctk.CTkButton(
            btn_frame, text="Cancel", fg_color="gray40",
            hover_color="gray30", command=self.destroy,
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")

    def _confirm(self) -> None:
        self._on_submit(self._name_entry.get())
        self.destroy()


class AddAssignmentDialog(ctk.CTkToplevel):

    def __init__(self, parent: ctk.CTk, student_name: str, on_submit):
        super().__init__(parent)
        self.title(f"New Assignment – {student_name}")
        self.geometry("440x320")
        self.resizable(False, False)
        self.grab_set()

        self._on_submit = on_submit
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Title (required):", anchor="w").grid(
            row=0, column=0, padx=20, pady=(20, 4), sticky="ew"
        )
        self._title_entry = ctk.CTkEntry(self, placeholder_text="e.g. Algebra exercises p. 45")
        self._title_entry.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="ew")
        self._title_entry.focus()

        ctk.CTkLabel(self, text="Description / notes (optional):", anchor="w").grid(
            row=2, column=0, padx=20, pady=(0, 4), sticky="ew"
        )
        self._desc_box = ctk.CTkTextbox(self, height=80)
        self._desc_box.grid(row=3, column=0, padx=20, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(self, text="Date assigned (YYYY-MM-DD):", anchor="w").grid(
            row=4, column=0, padx=20, pady=(0, 4), sticky="ew"
        )
        self._date_entry = ctk.CTkEntry(self, placeholder_text=date.today().isoformat())
        self._date_entry.insert(0, date.today().isoformat())
        self._date_entry.grid(row=5, column=0, padx=20, pady=(0, 16), sticky="ew")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_frame, text="Add Assignment", command=self._confirm).grid(
            row=0, column=0, padx=(0, 8), sticky="ew"
        )
        ctk.CTkButton(
            btn_frame, text="Cancel", fg_color="gray40",
            hover_color="gray30", command=self.destroy,
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")

    def _confirm(self) -> None:
        title = self._title_entry.get()
        description = self._desc_box.get("1.0", "end-1c")
        date_str = self._date_entry.get().strip()

        try:
            assigned_date = date.fromisoformat(date_str)
        except ValueError:
            messagebox.showerror(
                "Invalid date",
                f"'{date_str}' is not a valid date.\nPlease use the format YYYY-MM-DD.",
                parent=self,
            )
            return

        self._on_submit(title, description, assigned_date)
        self.destroy()

class AssignmentRow(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        assignment: dict,
        student_id: str,
        dm: DataManager,
        on_refresh,
    ):
        super().__init__(parent, corner_radius=8)
        self._assignment = assignment
        self._student_id = student_id
        self._dm = dm
        self._on_refresh = on_refresh
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        # Top bar: title + date + status badge
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, columnspan=2, padx=12, pady=(10, 2), sticky="ew")
        top_bar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top_bar,
            text=f"📋  {self._assignment['title']}",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            top_bar,
            text=f"📅 {self._assignment['date_assigned']}",
            text_color="gray70",
            font=ctk.CTkFont(size=11),
        ).grid(row=0, column=1, padx=(8, 0))

        status = self._assignment["status"]
        badge_color = COLOR_DONE if status == STATUS_DONE else COLOR_PENDING
        ctk.CTkLabel(
            top_bar,
            text=f"  {status}  ",
            fg_color=badge_color,
            corner_radius=6,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="white",
        ).grid(row=0, column=2, padx=(10, 0))

        # Description (if any)
        description = self._assignment.get("description", "")
        if description:
            ctk.CTkLabel(
                self,
                text=f"   {description}",
                anchor="w",
                text_color="gray60",
                font=ctk.CTkFont(size=11),
                wraplength=500,
            ).grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 4), sticky="ew")

        # Action buttons
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=2, column=0, columnspan=2, padx=12, pady=(4, 10), sticky="e")

        if status == STATUS_PENDING:
            ctk.CTkButton(
                action_frame,
                text="✔ Mark as Done",
                fg_color="#27ae60",
                hover_color="#1e8449",
                height=28,
                font=ctk.CTkFont(size=11),
                command=self._mark_done,
            ).pack(side="left", padx=(0, 6))
        else:
            ctk.CTkButton(
                action_frame,
                text="↩ Mark as Pending",
                fg_color="#e67e22",
                hover_color="#ca6f1e",
                height=28,
                font=ctk.CTkFont(size=11),
                command=self._mark_pending,
            ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            action_frame,
            text="🗑 Delete",
            fg_color="#c0392b",
            hover_color="#922b21",
            height=28,
            font=ctk.CTkFont(size=11),
            command=self._delete,
        ).pack(side="left")

    def _mark_done(self) -> None:
        try:
            self._dm.set_assignment_status(self._student_id, self._assignment["id"], STATUS_DONE)
            self._on_refresh()
        except (StudentNotFound, AssignmentNotFound, InvalidFieldValue) as e:
            messagebox.showerror("Error", str(e))

    def _mark_pending(self) -> None:
        try:
            self._dm.set_assignment_status(self._student_id, self._assignment["id"], STATUS_PENDING)
            self._on_refresh()
        except (StudentNotFound, AssignmentNotFound, InvalidFieldValue) as e:
            messagebox.showerror("Error", str(e))

    def _delete(self) -> None:
        confirmed = messagebox.askyesno(
            "Delete Assignment",
            f"Are you sure you want to delete:\n\"{self._assignment['title']}\"?",
        )
        if confirmed:
            try:
                self._dm.remove_assignment(self._student_id, self._assignment["id"])
                self._on_refresh()
            except (StudentNotFound, AssignmentNotFound) as e:
                messagebox.showerror("Error", str(e))

class StudentPanel(ctk.CTkFrame):

    def __init__(self, parent, dm: DataManager, on_student_select):
        super().__init__(parent, width=240, corner_radius=0)
        self.grid_propagate(False)
        self._dm = dm
        self._on_select = on_student_select
        self._selected_id: Optional[str] = None
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="👩‍🎓 Students",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(20, 8), sticky="w")

        self._search_entry = ctk.CTkEntry(self, placeholder_text="🔍 Search student...")
        self._search_entry.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="ew")
        self._search_entry.bind("<KeyRelease>", lambda e: self.refresh())

        self._list_frame = ctk.CTkScrollableFrame(self, label_text="")
        self._list_frame.grid(row=2, column=0, padx=8, pady=0, sticky="nsew")
        self._list_frame.grid_columnconfigure(0, weight=1)

        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.grid(row=3, column=0, padx=12, pady=12, sticky="ew")
        bottom_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            bottom_frame, text="+ Add Student", command=self._open_add_dialog
        ).grid(row=0, column=0, pady=(0, 6), sticky="ew")

        self._remove_btn = ctk.CTkButton(
            bottom_frame,
            text="🗑 Remove Student",
            fg_color="#c0392b",
            hover_color="#922b21",
            command=self._remove_student,
            state="disabled",
        )
        self._remove_btn.grid(row=1, column=0, sticky="ew")

    def refresh(self) -> None:
        """Rebuild the student list from the DataManager."""
        for widget in self._list_frame.winfo_children():
            widget.destroy()

        query = self._search_entry.get().strip().lower()
        students = [
            s for s in self._dm.get_all_students()
            if query in s["full_name"].lower()
        ]

        for student in students:
            is_selected = student["id"] == self._selected_id
            btn = ctk.CTkButton(
                self._list_frame,
                text=student["full_name"],
                fg_color="#1f538d" if is_selected else "transparent",
                hover_color="#1f538d",
                text_color="white" if is_selected else "gray80",
                anchor="w",
                command=lambda sid=student["id"]: self._select_student(sid),
            )
            btn.pack(fill="x", pady=2)

        self._remove_btn.configure(
            state="normal" if self._selected_id else "disabled"
        )

    def _select_student(self, student_id: str) -> None:
        self._selected_id = student_id
        self.refresh()
        self._on_select(student_id)

    def _open_add_dialog(self) -> None:
        AddStudentDialog(self, self._handle_add)

    def _handle_add(self, full_name: str) -> None:
        try:
            student = self._dm.add_student(full_name)
            self._selected_id = student["id"]
            self.refresh()
            self._on_select(student["id"])
        except InvalidFieldValue as e:
            messagebox.showerror("Error", str(e))

    def _remove_student(self) -> None:
        if not self._selected_id:
            return
        students = self._dm.get_all_students()
        name = next(
            (s["full_name"] for s in students if s["id"] == self._selected_id), "?"
        )
        confirmed = messagebox.askyesno(
            "Remove Student",
            f"Are you sure you want to remove:\n\"{name}\"?\n\n"
            "All their assignments will also be deleted!",
        )
        if confirmed:
            try:
                self._dm.remove_student(self._selected_id)
                self._selected_id = None
                self.refresh()
                self._on_select(None)
            except StudentNotFound as e:
                messagebox.showerror("Error", str(e))

    @property
    def selected_id(self) -> Optional[str]:
        return self._selected_id

class StudentDetailPanel(ctk.CTkFrame):

    def __init__(self, parent, dm: DataManager):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self._dm = dm
        self._student_id: Optional[str] = None
        self._status_filter = tk.StringVar(value="All")
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header card
        header_card = ctk.CTkFrame(self, corner_radius=10)
        header_card.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")
        header_card.grid_columnconfigure(0, weight=1)

        self._name_label = ctk.CTkLabel(
            header_card,
            text="← Select a student from the list on the left",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        self._name_label.grid(row=0, column=0, padx=16, pady=12, sticky="ew")

        self._stats_label = ctk.CTkLabel(
            header_card,
            text="",
            anchor="w",
            text_color="gray70",
        )
        self._stats_label.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="ew")

        # Toolbar
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=1, column=0, padx=16, pady=(0, 8), sticky="ew")

        ctk.CTkLabel(toolbar, text="Filter:").pack(side="left", padx=(0, 8))
        for option in ("All", STATUS_PENDING, STATUS_DONE):
            ctk.CTkRadioButton(
                toolbar,
                text=option,
                variable=self._status_filter,
                value=option,
                command=self._refresh_assignments,
            ).pack(side="left", padx=8)

        self._add_btn = ctk.CTkButton(
            toolbar,
            text="+ Add Assignment",
            state="disabled",
            command=self._open_add_dialog,
        )
        self._add_btn.pack(side="right")

        # Scrollable assignment list
        self._assignment_list = ctk.CTkScrollableFrame(self)
        self._assignment_list.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="nsew")
        self._assignment_list.grid_columnconfigure(0, weight=1)

    def load_student(self, student_id: Optional[str]) -> None:
        """Load a student's data into the panel, or reset when None."""
        self._student_id = student_id

        if student_id is None:
            self._name_label.configure(
                text="← Select a student from the list on the left"
            )
            self._stats_label.configure(text="")
            self._add_btn.configure(state="disabled")
            self._clear_assignments()
            return

        students = self._dm.get_all_students()
        student = next((s for s in students if s["id"] == student_id), None)
        if student is None:
            return

        self._name_label.configure(text=f"👤  {student['full_name']}")
        self._add_btn.configure(state="normal")
        self._refresh_stats()
        self._refresh_assignments()

    def _refresh_stats(self) -> None:
        if not self._student_id:
            return
        try:
            s = self._dm.get_student_stats(self._student_id)
            self._stats_label.configure(
                text=(
                    f"Total: {s['total']}   |   "
                    f"✔ Done: {s['done']}   |   "
                    f"✘ Pending: {s['pending']}   |   "
                    f"Completion rate: {s['completion_rate']}%"
                )
            )
        except StudentNotFound:
            pass

    def _refresh_assignments(self) -> None:
        if not self._student_id:
            return
        self._clear_assignments()
        try:
            assignments = self._dm.get_student_assignments(self._student_id)
        except StudentNotFound:
            return

        status_filter = self._status_filter.get()
        if status_filter != "All":
            assignments = [a for a in assignments if a["status"] == status_filter]

        if not assignments:
            ctk.CTkLabel(
                self._assignment_list,
                text="No assignments to display.",
                text_color="gray60",
                font=ctk.CTkFont(size=13),
            ).pack(pady=40)
            return

        for assignment in assignments:
            row = AssignmentRow(
                self._assignment_list,
                assignment,
                self._student_id,
                self._dm,
                self._on_assignment_changed,
            )
            row.pack(fill="x", pady=4)

    def _clear_assignments(self) -> None:
        for widget in self._assignment_list.winfo_children():
            widget.destroy()

    def _on_assignment_changed(self) -> None:
        """Called after any assignment mutation."""
        self._refresh_stats()
        self._refresh_assignments()

    def _open_add_dialog(self) -> None:
        if not self._student_id:
            return
        students = self._dm.get_all_students()
        student = next((s for s in students if s["id"] == self._student_id), None)
        if student:
            AddAssignmentDialog(self, student["full_name"], self._handle_add_assignment)

    def _handle_add_assignment(self, title: str, description: str, assigned_date: date) -> None:
        try:
            self._dm.add_assignment(self._student_id, title, description, assigned_date)
            self._on_assignment_changed()
        except (StudentNotFound, InvalidFieldValue) as e:
            messagebox.showerror("Error", str(e))

    def refresh(self) -> None:
        """Public refresh (e.g. after switching students)."""
        self.load_student(self._student_id)

class HomeworkTrackerApp(ctk.CTk):
    """
    Root window of the Homework Tracker application.

    Combines StudentPanel (sidebar) with StudentDetailPanel (main area).
    """

    def __init__(self, dm: DataManager) -> None:
        super().__init__()
        self._dm = dm
        self.title("📚 Homework Tracker – Tutor Dashboard")
        self.geometry("1100x720")
        self.minsize(800, 550)
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=3)

        # Left sidebar
        self._student_panel = StudentPanel(self, self._dm, self._on_student_selected)
        self._student_panel.grid(row=0, column=0, sticky="nsew")

        # Divider
        ctk.CTkFrame(self, width=2, fg_color="gray30").grid(
            row=0, column=1, sticky="ns"
        )

        # Main content
        self._detail_panel = StudentDetailPanel(self, self._dm)
        self._detail_panel.grid(row=0, column=2, sticky="nsew")

    def _on_student_selected(self, student_id: Optional[str]) -> None:
        """Callback fired when the user clicks a student in the sidebar."""
        self._detail_panel.load_student(student_id)
