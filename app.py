from __future__ import annotations
import tkinter as tk
from tkinter import messagebox
from datetime import date
from typing import Optional
import customtkinter as ctk
from date_picker import DateInput
from i18n import LANGUAGES, get_language, set_language, t
from data_manager import DatabaseError, DataManager, InvalidFieldValue, StudentNotFound, AssignmentNotFound, STATUS_DONE, STATUS_PENDING
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')
COLOR_DONE = '#2ecc71'
COLOR_PENDING = '#e74c3c'

class AddStudentDialog(ctk.CTkToplevel):

    def __init__(self, parent: ctk.CTk, on_submit):
        super().__init__(parent)
        self.title(t('add_student_title'))
        self.geometry('380x150')
        self.resizable(False, False)
        self.grab_set()
        self._on_submit = on_submit
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text=t('student_full_name'), anchor='w').grid(row=0, column=0, padx=20, pady=(20, 4), sticky='ew')
        self._name_entry = ctk.CTkEntry(self, placeholder_text=t('student_placeholder'))
        self._name_entry.grid(row=1, column=0, padx=20, pady=(0, 16), sticky='ew')
        self._name_entry.focus()
        btn_frame = ctk.CTkFrame(self, fg_color='transparent')
        btn_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky='ew')
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(btn_frame, text=t('add'), command=self._confirm).grid(row=0, column=0, padx=(0, 8), sticky='ew')
        ctk.CTkButton(btn_frame, text=t('cancel'), fg_color=('gray75', 'gray40'), hover_color=('gray65', 'gray30'), text_color=('gray10', 'white'), command=self.destroy).grid(row=0, column=1, padx=(8, 0), sticky='ew')

    def _confirm(self) -> None:
        if self._on_submit(self._name_entry.get()):
            self.destroy()

class AddAssignmentDialog(ctk.CTkToplevel):

    def __init__(self, parent: ctk.CTk, student_name: str, on_submit):
        super().__init__(parent)
        self.title(t('new_assignment_title', name=student_name))
        self.geometry('480x350')
        self.resizable(False, False)
        self.grab_set()
        self._on_submit = on_submit
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text=t('title_required'), anchor='w').grid(row=0, column=0, padx=20, pady=(20, 4), sticky='ew')
        self._title_entry = ctk.CTkEntry(self, placeholder_text=t('title_placeholder'))
        self._title_entry.grid(row=1, column=0, padx=20, pady=(0, 12), sticky='ew')
        self._title_entry.focus()
        ctk.CTkLabel(self, text=t('description_optional'), anchor='w').grid(row=2, column=0, padx=20, pady=(0, 4), sticky='ew')
        self._desc_box = ctk.CTkTextbox(self, height=75)
        self._desc_box.grid(row=3, column=0, padx=20, pady=(0, 12), sticky='ew')
        dates_frame = ctk.CTkFrame(self, fg_color='transparent')
        dates_frame.grid(row=4, column=0, padx=20, pady=(0, 16), sticky='ew')
        dates_frame.grid_columnconfigure((0, 1), weight=1)
        col_assigned = ctk.CTkFrame(dates_frame, fg_color='transparent')
        col_assigned.grid(row=0, column=0, padx=(0, 6), sticky='ew')
        col_assigned.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(col_assigned, text=t('date_assigned'), anchor='w').grid(row=0, column=0, sticky='w')
        self._assigned_input = DateInput(col_assigned, initial_date=date.today())
        self._assigned_input.grid(row=1, column=0, pady=(4, 0), sticky='ew')
        col_due = ctk.CTkFrame(dates_frame, fg_color='transparent')
        col_due.grid(row=0, column=1, padx=(6, 0), sticky='ew')
        col_due.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(col_due, text=t('due_date'), anchor='w').grid(row=0, column=0, sticky='w')
        self._due_input = DateInput(col_due, initial_date=date.today())
        self._due_input.grid(row=1, column=0, pady=(4, 0), sticky='ew')
        btn_frame = ctk.CTkFrame(self, fg_color='transparent')
        btn_frame.grid(row=5, column=0, padx=20, pady=(10, 16), sticky='ew')
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(btn_frame, text=t('add_assignment_confirm'), command=self._confirm).grid(row=0, column=0, padx=(0, 8), sticky='ew')
        ctk.CTkButton(btn_frame, text=t('cancel'), fg_color=('gray75', 'gray40'), hover_color=('gray65', 'gray30'), text_color=('gray10', 'white'), command=self.destroy).grid(row=0, column=1, padx=(8, 0), sticky='ew')

    def _confirm(self) -> None:
        title = self._title_entry.get()
        description = self._desc_box.get('1.0', 'end-1c')
        try:
            assigned_date = self._assigned_input.get_date()
            due_date = self._due_input.get_date()
        except InvalidFieldValue as exc:
            messagebox.showerror(t('invalid_date_title'), str(exc), parent=self)
            return
        if self._on_submit(title, description, assigned_date, due_date):
            self.destroy()

class EditAssignmentDialog(ctk.CTkToplevel):

    def __init__(self, parent: ctk.CTk, assignment: dict, on_submit):
        super().__init__(parent)
        self.title(t('edit_assignment_title'))
        self.geometry('480x370')
        self.resizable(False, False)
        self.grab_set()
        self._assignment = assignment
        self._on_submit = on_submit
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text=t('title_required'), anchor='w').grid(row=0, column=0, padx=20, pady=(20, 4), sticky='ew')
        self._title_entry = ctk.CTkEntry(self, placeholder_text=t('title_placeholder'))
        self._title_entry.insert(0, self._assignment.get('title', ''))
        self._title_entry.grid(row=1, column=0, padx=20, pady=(0, 12), sticky='ew')
        self._title_entry.focus()
        ctk.CTkLabel(self, text=t('description_optional'), anchor='w').grid(row=2, column=0, padx=20, pady=(0, 4), sticky='ew')
        self._desc_box = ctk.CTkTextbox(self, height=75)
        self._desc_box.insert('1.0', self._assignment.get('description', ''))
        self._desc_box.grid(row=3, column=0, padx=20, pady=(0, 12), sticky='ew')
        dates_frame = ctk.CTkFrame(self, fg_color='transparent')
        dates_frame.grid(row=4, column=0, padx=20, pady=(0, 16), sticky='ew')
        dates_frame.grid_columnconfigure((0, 1), weight=1)
        col_assigned = ctk.CTkFrame(dates_frame, fg_color='transparent')
        col_assigned.grid(row=0, column=0, padx=(0, 6), sticky='ew')
        col_assigned.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(col_assigned, text=t('date_assigned'), anchor='w').grid(row=0, column=0, sticky='w')
        try:
            initial_assigned = date.fromisoformat(self._assignment['date_assigned'])
        except (KeyError, ValueError, TypeError):
            initial_assigned = date.today()
        self._assigned_input = DateInput(col_assigned, initial_date=initial_assigned)
        self._assigned_input.grid(row=1, column=0, pady=(4, 0), sticky='ew')
        col_due = ctk.CTkFrame(dates_frame, fg_color='transparent')
        col_due.grid(row=0, column=1, padx=(6, 0), sticky='ew')
        col_due.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(col_due, text=t('due_date'), anchor='w').grid(row=0, column=0, sticky='w')
        try:
            initial_due = date.fromisoformat(self._assignment['due_date']) if self._assignment.get('due_date') else date.today()
        except (ValueError, TypeError):
            initial_due = date.today()
        self._due_input = DateInput(col_due, initial_date=initial_due)
        self._due_input.grid(row=1, column=0, pady=(4, 0), sticky='ew')
        btn_frame = ctk.CTkFrame(self, fg_color='transparent')
        btn_frame.grid(row=5, column=0, padx=20, pady=(10, 16), sticky='ew')
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(btn_frame, text=t('save_changes'), command=self._confirm).grid(row=0, column=0, padx=(0, 8), sticky='ew')
        ctk.CTkButton(btn_frame, text=t('cancel'), fg_color=('gray75', 'gray40'), hover_color=('gray65', 'gray30'), text_color=('gray10', 'white'), command=self.destroy).grid(row=0, column=1, padx=(8, 0), sticky='ew')

    def _confirm(self) -> None:
        title = self._title_entry.get()
        description = self._desc_box.get('1.0', 'end-1c')
        try:
            assigned_date = self._assigned_input.get_date()
            due_date = self._due_input.get_date()
        except InvalidFieldValue as exc:
            messagebox.showerror(t('invalid_date_title'), str(exc), parent=self)
            return
        if self._on_submit(title, description, assigned_date, due_date):
            self.destroy()

class AssignmentRow(ctk.CTkFrame):

    def __init__(self, parent, assignment: dict, student_id: str, dm: DataManager, on_refresh):
        super().__init__(parent, corner_radius=8)
        self._assignment = assignment
        self._student_id = student_id
        self._dm = dm
        self._on_refresh = on_refresh
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        top_bar = ctk.CTkFrame(self, fg_color='transparent')
        top_bar.grid(row=0, column=0, columnspan=2, padx=12, pady=(10, 2), sticky='ew')
        top_bar.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(top_bar, text=f"📋  {self._assignment['title']}", font=ctk.CTkFont(size=13, weight='bold'), anchor='w').grid(row=0, column=0, sticky='ew')
        dates_frame = ctk.CTkFrame(top_bar, fg_color='transparent')
        dates_frame.grid(row=0, column=1, padx=(8, 0))
        ctk.CTkLabel(dates_frame, text=f"📅 {self._assignment['date_assigned']}", text_color=('gray40', 'gray70'), font=ctk.CTkFont(size=11)).pack(side='left', padx=(0, 8))
        due_date = self._assignment.get('due_date')
        if due_date:
            status = self._assignment['status']
            is_overdue = (status == STATUS_PENDING) and (due_date < date.today().isoformat())
            due_color = ('#c0392b', '#e74c3c') if is_overdue else ('gray40', 'gray70')
            due_text = t('due', date=due_date, overdue=t('overdue') if is_overdue else '')
            ctk.CTkLabel(dates_frame, text=due_text, text_color=due_color, font=ctk.CTkFont(size=11, weight='bold' if is_overdue else 'normal')).pack(side='left')
        status = self._assignment['status']
        badge_color = COLOR_DONE if status == STATUS_DONE else COLOR_PENDING
        ctk.CTkLabel(top_bar, text=f"  {t('status_' + status)}  ", fg_color=badge_color, corner_radius=6, font=ctk.CTkFont(size=11, weight='bold'), text_color='white').grid(row=0, column=2, padx=(10, 0))
        description = self._assignment.get('description', '')
        if description:
            ctk.CTkLabel(self, text=f'   {description}', anchor='w', text_color=('gray40', 'gray60'), font=ctk.CTkFont(size=11), wraplength=500).grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 4), sticky='ew')
        action_frame = ctk.CTkFrame(self, fg_color='transparent')
        action_frame.grid(row=2, column=0, columnspan=2, padx=12, pady=(4, 10), sticky='e')
        ctk.CTkButton(action_frame, text=t('edit'), fg_color=('gray75', 'gray35'), hover_color=('gray65', 'gray25'), text_color=('gray10', 'white'), height=28, font=ctk.CTkFont(size=11), command=self._open_edit).pack(side='left', padx=(0, 6))
        if status == STATUS_PENDING:
            ctk.CTkButton(action_frame, text=t('mark_done'), fg_color='#27ae60', hover_color='#1e8449', text_color='white', height=28, font=ctk.CTkFont(size=11), command=self._mark_done).pack(side='left', padx=(0, 6))
        else:
            ctk.CTkButton(action_frame, text=t('mark_pending'), fg_color='#e67e22', hover_color='#ca6f1e', text_color='white', height=28, font=ctk.CTkFont(size=11), command=self._mark_pending).pack(side='left', padx=(0, 6))
        ctk.CTkButton(action_frame, text=t('delete'), fg_color='#c0392b', hover_color='#922b21', text_color='white', height=28, font=ctk.CTkFont(size=11), command=self._delete).pack(side='left')

    def _mark_done(self) -> None:
        try:
            self._dm.set_assignment_status(self._student_id, self._assignment['id'], STATUS_DONE)
            self._on_refresh()
        except (StudentNotFound, AssignmentNotFound, InvalidFieldValue, DatabaseError) as e:
            messagebox.showerror(t('error'), str(e))

    def _mark_pending(self) -> None:
        try:
            self._dm.set_assignment_status(self._student_id, self._assignment['id'], STATUS_PENDING)
            self._on_refresh()
        except (StudentNotFound, AssignmentNotFound, InvalidFieldValue, DatabaseError) as e:
            messagebox.showerror(t('error'), str(e))

    def _delete(self) -> None:
        confirmed = messagebox.askyesno(t('delete_assignment_title'), t('delete_assignment_confirm', title=self._assignment['title']))
        if confirmed:
            try:
                self._dm.remove_assignment(self._student_id, self._assignment['id'])
                self._on_refresh()
            except (StudentNotFound, AssignmentNotFound, DatabaseError) as e:
                messagebox.showerror(t('error'), str(e))

    def _open_edit(self) -> None:
        EditAssignmentDialog(self.winfo_toplevel(), self._assignment, self._save_edit)

    def _save_edit(self, title: str, description: str, assigned_date: date, due_date: date) -> bool:
        try:
            self._dm.update_assignment(self._student_id, self._assignment['id'], title, description, assigned_date, due_date)
            self._on_refresh()
            return True
        except (StudentNotFound, AssignmentNotFound, InvalidFieldValue, DatabaseError) as e:
            messagebox.showerror(t('error'), str(e))
            return False

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
        ctk.CTkLabel(self, text=t('students'), font=ctk.CTkFont(size=16, weight='bold')).grid(row=0, column=0, padx=16, pady=(20, 8), sticky='w')
        self._search_entry = ctk.CTkEntry(self, placeholder_text=t('search_student'))
        self._search_entry.grid(row=1, column=0, padx=12, pady=(0, 8), sticky='ew')
        self._search_entry.bind('<KeyRelease>', lambda e: self.refresh())
        self._list_frame = ctk.CTkScrollableFrame(self, label_text='')
        self._list_frame.grid(row=2, column=0, padx=8, pady=0, sticky='nsew')
        self._list_frame.grid_columnconfigure(0, weight=1)
        bottom_frame = ctk.CTkFrame(self, fg_color='transparent')
        bottom_frame.grid(row=3, column=0, padx=12, pady=12, sticky='ew')
        bottom_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(bottom_frame, text=t('add_student'), command=self._open_add_dialog).grid(row=0, column=0, pady=(0, 6), sticky='ew')
        self._remove_btn = ctk.CTkButton(bottom_frame, text=t('remove_student'), fg_color='#c0392b', hover_color='#922b21', text_color='white', command=self._remove_student, state='disabled')
        self._remove_btn.grid(row=1, column=0, sticky='ew')

    def refresh(self) -> None:
        for widget in self._list_frame.winfo_children():
            widget.destroy()
        query = self._search_entry.get().strip().lower()
        students = [s for s in self._dm.get_all_students() if query in s['full_name'].lower()]
        for student in students:
            is_selected = student['id'] == self._selected_id
            btn = ctk.CTkButton(self._list_frame, text=student['full_name'], fg_color='#1f538d' if is_selected else 'transparent', hover_color=('#3b8ed0', '#1f538d'), text_color='white' if is_selected else ('gray10', 'gray90'), anchor='w', command=lambda sid=student['id']: self._select_student(sid))
            btn.pack(fill='x', pady=2)
        self._remove_btn.configure(state='normal' if self._selected_id else 'disabled')

    def _select_student(self, student_id: str) -> None:
        self._selected_id = student_id
        self.refresh()
        self._on_select(student_id)

    def _open_add_dialog(self) -> None:
        AddStudentDialog(self, self._handle_add)

    def _handle_add(self, full_name: str) -> bool:
        try:
            student = self._dm.add_student(full_name)
            self._selected_id = student['id']
            self.refresh()
            self._on_select(student['id'])
            return True
        except (InvalidFieldValue, DatabaseError) as e:
            messagebox.showerror(t('error'), str(e))
            return False

    def _remove_student(self) -> None:
        if not self._selected_id:
            return
        students = self._dm.get_all_students()
        name = next((s['full_name'] for s in students if s['id'] == self._selected_id), '?')
        confirmed = messagebox.askyesno(t('remove_student_title'), t('remove_student_confirm', name=name))
        if confirmed:
            try:
                self._dm.remove_student(self._selected_id)
                self._selected_id = None
                self.refresh()
                self._on_select(None)
            except (StudentNotFound, DatabaseError) as e:
                messagebox.showerror(t('error'), str(e))

    @property
    def selected_id(self) -> Optional[str]:
        return self._selected_id

class StudentDetailPanel(ctk.CTkFrame):

    def __init__(self, parent, dm: DataManager):
        super().__init__(parent, corner_radius=0, fg_color='transparent')
        self._dm = dm
        self._student_id: Optional[str] = None
        self._status_filter = tk.StringVar(value='All')
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        header_card = ctk.CTkFrame(self, corner_radius=10)
        header_card.grid(row=0, column=0, padx=16, pady=(16, 8), sticky='ew')
        header_card.grid_columnconfigure(0, weight=1)
        self._name_label = ctk.CTkLabel(header_card, text=t('select_student_hint'), font=ctk.CTkFont(size=18, weight='bold'), anchor='w')
        self._name_label.grid(row=0, column=0, padx=16, pady=12, sticky='ew')
        self._stats_label = ctk.CTkLabel(header_card, text='', anchor='w', text_color=('gray40', 'gray70'))
        self._stats_label.grid(row=1, column=0, padx=16, pady=(0, 12), sticky='ew')
        toolbar = ctk.CTkFrame(self, fg_color='transparent')
        toolbar.grid(row=1, column=0, padx=16, pady=(0, 8), sticky='ew')
        ctk.CTkLabel(toolbar, text=t('filter')).pack(side='left', padx=(0, 8))
        for option, label in (('All', t('filter_all')), (STATUS_PENDING, t('status_Pending')), (STATUS_DONE, t('status_Done'))):
            ctk.CTkRadioButton(toolbar, text=label, variable=self._status_filter, value=option, command=self._refresh_assignments).pack(side='left', padx=8)
        self._add_btn = ctk.CTkButton(toolbar, text=t('add_assignment_btn'), state='disabled', command=self._open_add_dialog)
        self._add_btn.pack(side='right')
        self._assignment_list = ctk.CTkScrollableFrame(self)
        self._assignment_list.grid(row=2, column=0, padx=16, pady=(0, 16), sticky='nsew')
        self._assignment_list.grid_columnconfigure(0, weight=1)

    def load_student(self, student_id: Optional[str]) -> None:
        self._student_id = student_id
        if student_id is None:
            self._name_label.configure(text=t('select_student_hint'))
            self._stats_label.configure(text='')
            self._add_btn.configure(state='disabled')
            self._clear_assignments()
            return
        students = self._dm.get_all_students()
        student = next((s for s in students if s['id'] == student_id), None)
        if student is None:
            return
        self._name_label.configure(text=f"👤  {student['full_name']}")
        self._add_btn.configure(state='normal')
        self._refresh_stats()
        self._refresh_assignments()

    def _refresh_stats(self) -> None:
        if not self._student_id:
            return
        try:
            s = self._dm.get_student_stats(self._student_id)
            self._stats_label.configure(text=t('stats', total=s['total'], done=s['done'], pending=s['pending'], rate=s['completion_rate']))
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
        if status_filter != 'All':
            assignments = [a for a in assignments if a['status'] == status_filter]
        if not assignments:
            ctk.CTkLabel(self._assignment_list, text=t('no_assignments'), text_color=('gray40', 'gray60'), font=ctk.CTkFont(size=13)).pack(pady=40)
            return
        for assignment in assignments:
            row = AssignmentRow(self._assignment_list, assignment, self._student_id, self._dm, self._on_assignment_changed)
            row.pack(fill='x', pady=4)

    def _clear_assignments(self) -> None:
        for widget in self._assignment_list.winfo_children():
            widget.destroy()

    def _on_assignment_changed(self) -> None:
        self._refresh_stats()
        self._refresh_assignments()

    def _open_add_dialog(self) -> None:
        if not self._student_id:
            return
        students = self._dm.get_all_students()
        student = next((s for s in students if s['id'] == self._student_id), None)
        if student:
            AddAssignmentDialog(self, student['full_name'], self._handle_add_assignment)

    def _handle_add_assignment(self, title: str, description: str, assigned_date: date, due_date: date) -> bool:
        try:
            self._dm.add_assignment(self._student_id, title, description, assigned_date, due_date)
            self._on_assignment_changed()
            return True
        except (StudentNotFound, InvalidFieldValue, DatabaseError) as e:
            messagebox.showerror(t('error'), str(e))
            return False

    def refresh(self) -> None:
        self.load_student(self._student_id)

class HomeworkTrackerApp(ctk.CTk):

    def __init__(self, dm: DataManager) -> None:
        super().__init__()
        self._dm = dm
        self.title(t('app_title'))
        self.geometry('1100x720')
        self.minsize(800, 550)
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=3)
        self._student_panel = StudentPanel(self, self._dm, self._on_student_selected)
        self._student_panel.grid(row=0, column=0, sticky='nsew')
        self._separator = ctk.CTkFrame(self, width=2, fg_color=('gray80', 'gray30'))
        self._separator.grid(row=0, column=1, sticky='ns')
        self._detail_panel = StudentDetailPanel(self, self._dm)
        self._detail_panel.grid(row=0, column=2, sticky='nsew')
        self._build_settings()

    def _build_settings(self) -> None:
        self._settings_frame = ctk.CTkFrame(self, corner_radius=8, border_width=1, border_color=('gray70', 'gray35'))
        self._settings_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self._settings_frame, text=t('theme'), font=ctk.CTkFont(size=12), anchor='w').grid(row=0, column=0, padx=10, pady=(8, 2), sticky='ew')
        theme_switch = ctk.CTkSegmentedButton(self._settings_frame, values=[t('theme_dark'), t('theme_light')], command=self._on_theme_change)
        theme_switch.set(t('theme_dark') if ctk.get_appearance_mode().lower() == 'dark' else t('theme_light'))
        theme_switch.grid(row=1, column=0, padx=10, sticky='ew')
        ctk.CTkLabel(self._settings_frame, text=t('language'), font=ctk.CTkFont(size=12), anchor='w').grid(row=2, column=0, padx=10, pady=(8, 2), sticky='ew')
        lang_switch = ctk.CTkSegmentedButton(self._settings_frame, values=list(LANGUAGES.values()), command=self._on_language_change)
        lang_switch.set(LANGUAGES[get_language()])
        lang_switch.grid(row=3, column=0, padx=10, pady=(0, 10), sticky='ew')
        self._settings_visible = False
        self._settings_btn = ctk.CTkButton(self, text='⚙', width=34, height=34, font=ctk.CTkFont(size=18), fg_color=('gray75', 'gray30'), hover_color=('gray65', 'gray40'), text_color=('gray10', 'white'), command=self._toggle_settings)
        self._settings_btn.place(relx=1.0, x=-26, y=26, anchor='ne')

    def _toggle_settings(self) -> None:
        self._settings_visible = not self._settings_visible
        if self._settings_visible:
            self._settings_frame.place(relx=1.0, x=-26, y=68, anchor='ne')
            self._settings_frame.lift()
        else:
            self._settings_frame.place_forget()

    def _on_theme_change(self, mode: str) -> None:
        ctk.set_appearance_mode('dark' if mode == t('theme_dark') else 'light')
        self._student_panel.refresh()

    def _on_language_change(self, label: str) -> None:
        code = next((c for c, name in LANGUAGES.items() if name == label), None)
        if code and code != get_language():
            set_language(code)
            self._rebuild_for_language()

    def _rebuild_for_language(self) -> None:
        selected = self._student_panel.selected_id
        self.after(0, lambda: self._do_rebuild(selected))

    def _do_rebuild(self, selected: Optional[str]) -> None:
        for widget in (self._student_panel, self._separator, self._detail_panel, self._settings_frame, self._settings_btn):
            widget.destroy()
        self.title(t('app_title'))
        self._build_ui()
        if selected:
            self._student_panel._selected_id = selected
            self._student_panel.refresh()
            self._detail_panel.load_student(selected)
        else:
            self._detail_panel.load_student(None)

    def _on_student_selected(self, student_id: Optional[str]) -> None:
        self._detail_panel.load_student(student_id)
