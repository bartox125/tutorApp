from __future__ import annotations
import json
import os
import tempfile
from contextlib import contextmanager
from copy import deepcopy
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

class DatabaseError(Exception):
    pass

def _serialize_date(d: date) -> str:
    return d.isoformat()

def _deserialize_date(s: str) -> date:
    return date.fromisoformat(s)

class DataManager:

    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self._db_path = Path(db_path)
        self._data: dict[str, Any] = {'students': {}}
        self._load()

    def _load(self) -> None:
        try:
            with open(self._db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            return
        except (OSError, ValueError) as exc:
            raise DatabaseError(
                f"Could not load database '{self._db_path}': {exc}. "
                'The file has been left unchanged. Restore or repair it before restarting.'
            ) from exc
        try:
            self._validate_data(data)
        except (ValueError, TypeError) as exc:
            raise DatabaseError(
                f"Invalid database '{self._db_path}': {exc}. "
                'The file has been left unchanged. Restore or repair it before restarting.'
            ) from exc
        self._data = data

    @staticmethod
    def _validate_data(data: Any) -> None:
        def require_date(value: Any, field: str) -> None:
            if not isinstance(value, str):
                raise ValueError(f'{field} must be a date in YYYY-MM-DD format')
            try:
                parsed = _deserialize_date(value)
            except ValueError as exc:
                raise ValueError(f'{field} must be a valid date in YYYY-MM-DD format') from exc
            if parsed.isoformat() != value:
                raise ValueError(f'{field} must use YYYY-MM-DD format')

        if not isinstance(data, dict) or not isinstance(data.get('students'), dict):
            raise ValueError("'students' must be an object")
        for student_id, student in data['students'].items():
            if not isinstance(student, dict) or student.get('id') != student_id:
                raise ValueError(f'Invalid student record: {student_id}')
            name = student.get('full_name')
            if not isinstance(name, str) or not name.strip():
                raise ValueError(f'Invalid student name: {student_id}')
            require_date(student.get('date_added'), 'date_added')
            assignments = student.get('assignments')
            if not isinstance(assignments, dict):
                raise ValueError(f'Assignments must be an object: {student_id}')
            for assignment_id, assignment in assignments.items():
                if not isinstance(assignment, dict) or assignment.get('id') != assignment_id:
                    raise ValueError(f'Invalid assignment record: {assignment_id}')
                title = assignment.get('title')
                if not isinstance(title, str) or not title.strip():
                    raise ValueError(f'Invalid assignment title: {assignment_id}')
                if not isinstance(assignment.get('description', ''), str):
                    raise ValueError(f'Invalid assignment description: {assignment_id}')
                require_date(assignment.get('date_assigned'), 'date_assigned')
                if assignment.get('due_date') is not None:
                    require_date(assignment['due_date'], 'due_date')
                if assignment.get('status') not in (STATUS_PENDING, STATUS_DONE):
                    raise ValueError(f'Invalid assignment status: {assignment_id}')

    def _save(self) -> None:
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode='w', encoding='utf-8', dir=self._db_path.parent,
                prefix=f'.{self._db_path.name}.', suffix='.tmp', delete=False
            ) as f:
                temp_path = Path(f.name)
                json.dump(self._data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, self._db_path)
        except (OSError, ValueError, TypeError) as exc:
            raise DatabaseError(f"Could not save database '{self._db_path}': {exc}") from exc
        finally:
            if temp_path is not None:
                try:
                    temp_path.unlink(missing_ok=True)
                except OSError:
                    pass

    @contextmanager
    def _transaction(self):
        previous = self._data
        self._data = deepcopy(previous)
        try:
            yield
            self._save()
        except Exception:
            self._data = previous
            raise

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
        with self._transaction():
            self._data['students'][student_id] = student
        return student

    def remove_student(self, student_id: str) -> None:
        self._get_student(student_id)
        with self._transaction():
            del self._data['students'][student_id]

    def get_all_students(self) -> list[dict]:
        return sorted(self._data['students'].values(), key=lambda s: s['full_name'].lower())

    def _get_student(self, student_id: str) -> dict:
        student = self._data['students'].get(student_id)
        if student is None:
            raise StudentNotFound(f"Student with ID '{student_id}' does not exist.")
        return student

    def add_assignment(self, student_id: str, title: str, description: str = '', date_assigned: date | None = None, due_date: date | None = None) -> dict:
        student = self._get_student(student_id)
        title = self._validate_text(title, 'Title')
        if date_assigned is None:
            date_assigned = date.today()
        assignment_id = str(uuid.uuid4())
        assignment = {
            'id': assignment_id,
            'title': title,
            'description': description.strip(),
            'date_assigned': _serialize_date(date_assigned),
            'due_date': _serialize_date(due_date) if due_date else None,
            'status': STATUS_PENDING
        }
        with self._transaction():
            self._get_student(student_id)['assignments'][assignment_id] = assignment
        return assignment

    def remove_assignment(self, student_id: str, assignment_id: str) -> None:
        student = self._get_student(student_id)
        if assignment_id not in student['assignments']:
            raise AssignmentNotFound(f"Assignment with ID '{assignment_id}' does not exist.")
        with self._transaction():
            del self._get_student(student_id)['assignments'][assignment_id]

    def set_assignment_status(self, student_id: str, assignment_id: str, new_status: str) -> dict:
        if new_status not in (STATUS_DONE, STATUS_PENDING):
            raise InvalidFieldValue(f"Invalid status: '{new_status}'. Allowed values: '{STATUS_DONE}', '{STATUS_PENDING}'.")
        student = self._get_student(student_id)
        assignment = student['assignments'].get(assignment_id)
        if assignment is None:
            raise AssignmentNotFound(f"Assignment with ID '{assignment_id}' does not exist.")
        with self._transaction():
            assignment = self._get_student(student_id)['assignments'][assignment_id]
            assignment['status'] = new_status
        return assignment

    def get_student_assignments(self, student_id: str) -> list[dict]:
        student = self._get_student(student_id)
        return sorted(student['assignments'].values(), key=lambda a: a['date_assigned'], reverse=True)

    def update_assignment(self, student_id: str, assignment_id: str, title: str, description: str, date_assigned: date, due_date: date | None) -> dict:
        title = self._validate_text(title, 'Title')
        student = self._get_student(student_id)
        if assignment_id not in student['assignments']:
            raise AssignmentNotFound(f"Assignment with ID '{assignment_id}' does not exist.")
        with self._transaction():
            assignment = self._get_student(student_id)['assignments'][assignment_id]
            assignment['title'] = title
            assignment['description'] = description.strip()
            assignment['date_assigned'] = _serialize_date(date_assigned)
            assignment['due_date'] = _serialize_date(due_date) if due_date else None
        return self._get_student(student_id)['assignments'][assignment_id]

    def get_student_stats(self, student_id: str) -> dict:
        assignments = self.get_student_assignments(student_id)
        total = len(assignments)
        done = sum((1 for a in assignments if a['status'] == STATUS_DONE))
        pending = total - done
        rate = round(done / total * 100 if total > 0 else 0.0, 1)
        return {'total': total, 'done': done, 'pending': pending, 'completion_rate': rate}
