import json
import tempfile
import unittest
from copy import deepcopy
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import main
from app import AddAssignmentDialog, AddStudentDialog, AssignmentRow, StudentDetailPanel, StudentPanel
from data_manager import DatabaseError, DataManager, InvalidFieldValue, STATUS_DONE, STATUS_PENDING
from date_picker import DateInput


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'homework_data.json'
        self.dm = DataManager(self.path)

    def seed(self):
        student = self.dm.add_student('Alice')
        assignment = self.dm.add_assignment(student['id'], 'Algebra', 'Notes', date(2026, 2, 1), date(2026, 2, 7))
        return student, assignment

    def test_missing_database_starts_empty_without_creating_file(self):
        self.assertEqual(self.dm.get_all_students(), [])
        self.assertFalse(self.path.exists())

    def test_successful_changes_survive_reload(self):
        student, assignment = self.seed()
        self.dm.set_assignment_status(student['id'], assignment['id'], STATUS_DONE)
        loaded = DataManager(self.path)
        self.assertEqual(loaded.get_student_stats(student['id'])['done'], 1)
        self.assertEqual(loaded.get_student_assignments(student['id'])[0]['due_date'], '2026-02-07')
        loaded.remove_assignment(student['id'], assignment['id'])
        self.assertEqual(DataManager(self.path).get_student_stats(student['id'])['total'], 0)
        loaded.remove_student(student['id'])
        self.assertEqual(DataManager(self.path).get_all_students(), [])
        self.assertEqual(list(self.path.parent.glob('*.tmp')), [])

    def test_every_failed_mutation_preserves_disk_memory_and_existing_references(self):
        student, assignment = self.seed()
        operations = [
            lambda: self.dm.add_student('Bob'),
            lambda: self.dm.remove_student(student['id']),
            lambda: self.dm.add_assignment(student['id'], 'Geometry'),
            lambda: self.dm.remove_assignment(student['id'], assignment['id']),
            lambda: self.dm.set_assignment_status(student['id'], assignment['id'], STATUS_DONE),
        ]
        original_bytes = self.path.read_bytes()
        original_data = deepcopy(self.dm.get_all_students())
        current_student = self.dm.get_all_students()[0]
        current_assignment = self.dm.get_student_assignments(student['id'])[0]
        for operation in operations:
            with self.subTest(operation=operation), patch('data_manager.os.replace', side_effect=PermissionError('locked')):
                with self.assertRaises(DatabaseError):
                    operation()
                self.assertEqual(self.path.read_bytes(), original_bytes)
                self.assertEqual(self.dm.get_all_students(), original_data)
                self.assertEqual(current_assignment['status'], STATUS_PENDING)
                self.assertIn(assignment['id'], current_student['assignments'])
                self.assertEqual(list(self.path.parent.glob('*.tmp')), [])
        self.dm.add_student('Bob')
        self.assertEqual(len(DataManager(self.path).get_all_students()), 2)

    def test_partial_write_cannot_truncate_original_database(self):
        self.seed()
        original_bytes = self.path.read_bytes()
        original_data = deepcopy(self.dm.get_all_students())

        def partial_write(data, stream, **kwargs):
            stream.write('{')
            raise OSError('disk full')

        with patch('data_manager.json.dump', side_effect=partial_write):
            with self.assertRaises(DatabaseError):
                self.dm.add_student('Bob')
        self.assertEqual(self.path.read_bytes(), original_bytes)
        self.assertEqual(self.dm.get_all_students(), original_data)
        self.assertEqual(list(self.path.parent.glob('*.tmp')), [])

    def test_fsync_failure_preserves_original_database(self):
        self.seed()
        original_bytes = self.path.read_bytes()
        with patch('data_manager.os.fsync', side_effect=OSError('disk error')):
            with self.assertRaises(DatabaseError):
                self.dm.add_student('Bob')
        self.assertEqual(self.path.read_bytes(), original_bytes)
        self.assertEqual(len(self.dm.get_all_students()), 1)
        self.assertEqual(list(self.path.parent.glob('*.tmp')), [])

    def test_failed_first_save_does_not_leave_a_database(self):
        with patch('data_manager.tempfile.NamedTemporaryFile', side_effect=PermissionError('read-only')):
            with self.assertRaises(DatabaseError):
                self.dm.add_student('Alice')
        self.assertFalse(self.path.exists())
        self.assertEqual(self.dm.get_all_students(), [])

    def test_corrupt_or_wrongly_encoded_database_is_preserved(self):
        for content in (b'{"students":', b'\xff\xfe'):
            with self.subTest(content=content):
                self.path.write_bytes(content)
                with self.assertRaises(DatabaseError):
                    DataManager(self.path)
                self.assertEqual(self.path.read_bytes(), content)

    def test_invalid_top_level_structure_is_rejected(self):
        for payload in ({}, [], None, {'students': []}, {'students': {'s': None}}):
            with self.subTest(payload=payload):
                content = json.dumps(payload)
                self.path.write_text(content, encoding='utf-8')
                with self.assertRaises(DatabaseError):
                    DataManager(self.path)
                self.assertEqual(self.path.read_text(encoding='utf-8'), content)

    def test_invalid_nested_fields_are_rejected(self):
        student, assignment = self.seed()
        original = json.loads(self.path.read_text(encoding='utf-8'))
        changes = [
            ('student', 'id', 'wrong'), ('student', 'full_name', 12),
            ('student', 'date_added', '2026-02-30'), ('student', 'assignments', []),
            ('assignment', 'id', 'wrong'), ('assignment', 'title', ''),
            ('assignment', 'description', []), ('assignment', 'status', 'Unknown'),
            ('assignment', 'date_assigned', '20260201'), ('assignment', 'due_date', 42),
        ]
        for target, key, value in changes:
            with self.subTest(target=target, key=key):
                payload = deepcopy(original)
                record = payload['students'][student['id']]
                if target == 'assignment':
                    record = record['assignments'][assignment['id']]
                record[key] = value
                content = json.dumps(payload)
                self.path.write_text(content, encoding='utf-8')
                with self.assertRaises(DatabaseError):
                    DataManager(self.path)
                self.assertEqual(self.path.read_text(encoding='utf-8'), content)

    def test_older_assignment_without_optional_fields_loads(self):
        student, assignment = self.seed()
        payload = json.loads(self.path.read_text(encoding='utf-8'))
        record = payload['students'][student['id']]['assignments'][assignment['id']]
        del record['due_date']
        del record['description']
        self.path.write_text(json.dumps(payload), encoding='utf-8')
        self.assertEqual(DataManager(self.path).get_student_stats(student['id'])['total'], 1)

    def test_read_failure_is_reported(self):
        with patch('builtins.open', side_effect=PermissionError('read denied')):
            with self.assertRaises(DatabaseError):
                DataManager(self.path)


class FormTests(unittest.TestCase):
    def date_input(self, text):
        widget = SimpleNamespace(_entry=Mock(), _date=date(2026, 2, 1), _on_change=Mock())
        widget._entry.get.return_value = text
        widget.get_date = lambda: DateInput.get_date(widget)
        return widget

    def assignment_dialog(self):
        return SimpleNamespace(
            _title_entry=Mock(), _desc_box=Mock(), _assigned_input=Mock(),
            _due_input=Mock(), _on_submit=Mock(return_value=True), destroy=Mock(),
        )

    def test_invalid_dates_are_rejected_and_preserved(self):
        for text in ('2026-02-30', '', 'tomorrow', '20260201', '2026-W05-7'):
            with self.subTest(text=text):
                widget = self.date_input(text)
                with self.assertRaises(InvalidFieldValue):
                    widget.get_date()
                DateInput._on_entry_focus_out(widget)
                widget._entry.delete.assert_not_called()
                widget._on_change.assert_not_called()
                self.assertEqual(widget._date, date(2026, 2, 1))

    def test_valid_date_updates_state_and_clears_error(self):
        widget = self.date_input('2028-02-29')
        DateInput._on_entry_focus_out(widget)
        self.assertEqual(widget._date, date(2028, 2, 29))
        widget._on_change.assert_called_once_with(date(2028, 2, 29))
        widget._entry.configure.assert_called_with(border_width=0)

    def test_invalid_date_blocks_assignment_submission(self):
        for field in ('_assigned_input', '_due_input'):
            with self.subTest(field=field):
                dialog = self.assignment_dialog()
                getattr(dialog, field).get_date.side_effect = InvalidFieldValue('Invalid date')
                with patch('app.messagebox.showerror') as showerror:
                    AddAssignmentDialog._confirm(dialog)
                showerror.assert_called_once()
                dialog._on_submit.assert_not_called()
                dialog.destroy.assert_not_called()

    def test_both_dialogs_close_only_on_success(self):
        for accepted in (False, True):
            with self.subTest(accepted=accepted):
                student_dialog = SimpleNamespace(_name_entry=Mock(), _on_submit=Mock(return_value=accepted), destroy=Mock())
                assignment_dialog = self.assignment_dialog()
                assignment_dialog._on_submit.return_value = accepted
                AddStudentDialog._confirm(student_dialog)
                AddAssignmentDialog._confirm(assignment_dialog)
                self.assertEqual(student_dialog.destroy.called, accepted)
                self.assertEqual(assignment_dialog.destroy.called, accepted)

    def test_submission_handlers_report_validation_and_save_errors(self):
        for error in (InvalidFieldValue('Required'), DatabaseError('Save failed')):
            with self.subTest(error=error):
                panel = SimpleNamespace(_dm=Mock(), _selected_id='existing', refresh=Mock(), _on_select=Mock())
                panel._dm.add_student.side_effect = error
                detail = SimpleNamespace(_dm=Mock(), _student_id='s', _on_assignment_changed=Mock())
                detail._dm.add_assignment.side_effect = error
                with patch('app.messagebox.showerror') as showerror:
                    self.assertFalse(StudentPanel._handle_add(panel, ''))
                    self.assertFalse(StudentDetailPanel._handle_add_assignment(detail, '', 'notes', date.today(), date.today()))
                self.assertEqual(showerror.call_count, 2)
                self.assertEqual(panel._selected_id, 'existing')
                panel.refresh.assert_not_called()
                detail._on_assignment_changed.assert_not_called()

    def test_status_and_delete_failures_show_errors_without_refreshing(self):
        for method, operation in (('_mark_done', 'set_assignment_status'), ('_mark_pending', 'set_assignment_status'), ('_delete', 'remove_assignment')):
            with self.subTest(method=method):
                row = SimpleNamespace(_dm=Mock(), _student_id='s', _assignment={'id': 'a', 'title': 'Task'}, _on_refresh=Mock())
                getattr(row._dm, operation).side_effect = DatabaseError('Save failed')
                with patch('app.messagebox.askyesno', return_value=True), patch('app.messagebox.showerror') as showerror:
                    getattr(AssignmentRow, method)(row)
                showerror.assert_called_once()
                row._on_refresh.assert_not_called()

    def test_student_delete_failure_keeps_selection(self):
        panel = SimpleNamespace(_dm=Mock(), _selected_id='s', refresh=Mock(), _on_select=Mock())
        panel._dm.get_all_students.return_value = [{'id': 's', 'full_name': 'Alice'}]
        panel._dm.remove_student.side_effect = DatabaseError('Save failed')
        with patch('app.messagebox.askyesno', return_value=True), patch('app.messagebox.showerror') as showerror:
            StudentPanel._remove_student(panel)
        showerror.assert_called_once()
        self.assertEqual(panel._selected_id, 's')
        panel.refresh.assert_not_called()
        panel._on_select.assert_not_called()

    def test_startup_reports_database_error_and_does_not_open_dashboard(self):
        with patch('main.DataManager', side_effect=DatabaseError('Invalid database')), patch('main.tk.Tk') as root, patch('main.messagebox.showerror') as showerror, patch('main.HomeworkTrackerApp') as app:
            main.main()
        showerror.assert_called_once()
        root.return_value.destroy.assert_called_once()
        app.assert_not_called()


if __name__ == '__main__':
    unittest.main()
