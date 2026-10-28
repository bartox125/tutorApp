from __future__ import annotations
import json
import uuid
from datetime import date
from pathlib import Path
from typing import Any
DEFAULT_DB_PATH = Path('homework_data.json')
STATUS_PENDING = 'Pending'
STATUS_DONE = 'Done'

class StudentNotFound(Exception):
    pass

class AssignmentNotFound(Exception):
    pass

class InvalidFieldValue(ValueError):
    pass

def _serialize_date(d: date) -> str:
    return d.isoformat()

def _deserialize_date(s: str) -> date:
    return date.fromisoformat(s)

class DataManager:

    def __init__(self, db_path: Path=DEFAULT_DB_PATH) -> None:
        self._db_path = Path(db_path)
        self._data: dict[str, Any] = {'students': {}}
        self._load()

    def _load(self) -> None:
        if self._db_path.exists():
            try:
                with open(self._db_path, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, OSError) as exc:
                print(f'[WARNING] Could not load database file: {exc}')
                self._data = {'students': {}}

    def _save(self) -> None:
        try:
            with open(self._db_path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except OSError as exc:
            print(f'[ERROR] Could not save database file: {exc}')

    @staticmethod
    def _validate_text(value: str, field_name: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise InvalidFieldValue(f"Field '{field_name}' must not be empty.")
        return stripped

    def add_student(self, full_name: str) -> dict:
        full_name = self._validate_text(full_name, 'Full name')
        student_id = str(uuid.uuid4())
        student = {'id': student_id, 'full_name': full_name, 'date_added': _serialize_date(date.today()), 'assignments': {}}
        self._data['students'][student_id] = student
        self._save()
        return student

    def remove_student(self, student_id: str) -> None:
        self._get_student(student_id)
        del self._data['students'][student_id]
        self._save()

    def get_all_students(self) -> list[dict]:
        return sorted(self._data['students'].values(), key=lambda s: s['full_name'].lower())

    def _get_student(self, student_id: str) -> dict:
        student = self._data['students'].get(student_id)
        if student is None:
            raise StudentNotFound(f"Student with ID '{student_id}' does not exist.")
        return student

    def add_assignment(self, student_id: str, title: str, description: str='', date_assigned: date | None=None) -> dict:
        student = self._get_student(student_id)
        title = self._validate_text(title, 'Title')
        if date_assigned is None:
            date_assigned = date.today()
        assignment_id = str(uuid.uuid4())
        assignment = {'id': assignment_id, 'title': title, 'description': description.strip(), 'date_assigned': _serialize_date(date_assigned), 'status': STATUS_PENDING}
        student['assignments'][assignment_id] = assignment
        self._save()
        return assignment

    def remove_assignment(self, student_id: str, assignment_id: str) -> None:
        student = self._get_student(student_id)
        if assignment_id not in student['assignments']:
            raise AssignmentNotFound(f"Assignment with ID '{assignment_id}' does not exist.")
        del student['assignments'][assignment_id]
        self._save()

    def set_assignment_status(self, student_id: str, assignment_id: str, new_status: str) -> dict:
        if new_status not in (STATUS_DONE, STATUS_PENDING):
            raise InvalidFieldValue(f"Invalid status: '{new_status}'. Allowed values: '{STATUS_DONE}', '{STATUS_PENDING}'.")
        student = self._get_student(student_id)
        assignment = student['assignments'].get(assignment_id)
        if assignment is None:
            raise AssignmentNotFound(f"Assignment with ID '{assignment_id}' does not exist.")
        assignment['status'] = new_status
        self._save()
        return assignment

    def get_student_assignments(self, student_id: str) -> list[dict]:
        student = self._get_student(student_id)
        return sorted(student['assignments'].values(), key=lambda a: a['date_assigned'], reverse=True)

    def get_student_stats(self, student_id: str) -> dict:
        assignments = self.get_student_assignments(student_id)
        total = len(assignments)
        done = sum((1 for a in assignments if a['status'] == STATUS_DONE))
        pending = total - done
        rate = round(done / total * 100 if total > 0 else 0.0, 1)
        return {'total': total, 'done': done, 'pending': pending, 'completion_rate': rate}
