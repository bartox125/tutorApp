"""Lightweight translations (Polish / English) with a persisted language choice."""
from __future__ import annotations
import json
from pathlib import Path

SETTINGS_PATH = Path('settings.json')
LANGUAGES = {'pl': 'Polski', 'en': 'English'}
DEFAULT_LANGUAGE = 'pl'

_STRINGS: dict[str, dict[str, str]] = {
    'en': {
        'app_title': '📚 Homework Tracker – Tutor Dashboard',
        'students': '👩‍🎓 Students',
        'search_student': '🔍 Search student...',
        'add_student': '+ Add Student',
        'remove_student': '🗑 Remove Student',
        'theme': 'Theme:',
        'theme_dark': 'Dark',
        'theme_light': 'Light',
        'language': 'Language:',
        'select_student_hint': '← Select a student from the list on the left',
        'filter': 'Filter:',
        'filter_all': 'All',
        'add_assignment_btn': '+ Add Assignment',
        'no_assignments': 'No assignments to display.',
        'stats': 'Total: {total}   |   ✔ Done: {done}   |   ✘ Pending: {pending}   |   Completion rate: {rate}%',
        'status_Pending': 'Pending',
        'status_Done': 'Done',
        'overdue': ' (Overdue)',
        'due': '⏰ Due: {date}{overdue}',
        'edit': '✏ Edit',
        'mark_done': '✔ Mark as Done',
        'mark_pending': '↩ Mark as Pending',
        'delete': '🗑 Delete',
        'add': 'Add',
        'cancel': 'Cancel',
        'error': 'Error',
        'invalid_date_title': 'Invalid date',
        'add_student_title': 'Add Student',
        'student_full_name': "Student's full name:",
        'student_placeholder': 'e.g. Anna Smith',
        'new_assignment_title': 'New Assignment – {name}',
        'edit_assignment_title': 'Edit Assignment',
        'title_required': 'Title (required):',
        'title_placeholder': 'e.g. Algebra exercises p. 45',
        'description_optional': 'Description / notes (optional):',
        'date_assigned': 'Date assigned:',
        'due_date': 'Due date:',
        'add_assignment_confirm': 'Add Assignment',
        'save_changes': 'Save Changes',
        'delete_assignment_title': 'Delete Assignment',
        'delete_assignment_confirm': 'Are you sure you want to delete:\n"{title}"?',
        'remove_student_title': 'Remove Student',
        'remove_student_confirm': 'Are you sure you want to remove:\n"{name}"?\n\nAll their assignments will also be deleted!',
        'select_date': 'Select Date',
        'today': 'Today',
        'weekdays': 'Mo,Tu,We,Th,Fr,Sa,Su',
        'months': 'January,February,March,April,May,June,July,August,September,October,November,December',
        'db_error_title': 'Database error',
        # data layer messages
        'err_empty_field': "Field '{field}' must not be empty.",
        'field_full_name': 'Full name',
        'field_title': 'Title',
        'err_student_missing': "Student with ID '{id}' does not exist.",
        'err_assignment_missing': "Assignment with ID '{id}' does not exist.",
        'err_invalid_status': "Invalid status: '{status}'. Allowed values: '{done}', '{pending}'.",
        'err_invalid_date': "Invalid date '{value}'. Enter a valid date in YYYY-MM-DD format.",
        'err_load': "Could not load database '{path}': {error}. The file has been left unchanged. Restore or repair it before restarting.",
        'err_invalid_db': "Invalid database '{path}': {error}. The file has been left unchanged. Restore or repair it before restarting.",
        'err_save': "Could not save database '{path}': {error}",
    },
    'pl': {
        'app_title': '📚 Dziennik prac domowych – Panel korepetytora',
        'students': '👩‍🎓 Uczniowie',
        'search_student': '🔍 Szukaj ucznia...',
        'add_student': '+ Dodaj ucznia',
        'remove_student': '🗑 Usuń ucznia',
        'theme': 'Motyw:',
        'theme_dark': 'Ciemny',
        'theme_light': 'Jasny',
        'language': 'Język:',
        'select_student_hint': '← Wybierz ucznia z listy po lewej',
        'filter': 'Filtr:',
        'filter_all': 'Wszystkie',
        'add_assignment_btn': '+ Dodaj zadanie',
        'no_assignments': 'Brak zadań do wyświetlenia.',
        'stats': 'Razem: {total}   |   ✔ Zrobione: {done}   |   ✘ Do zrobienia: {pending}   |   Wykonanie: {rate}%',
        'status_Pending': 'Do zrobienia',
        'status_Done': 'Zrobione',
        'overdue': ' (Po terminie)',
        'due': '⏰ Termin: {date}{overdue}',
        'edit': '✏ Edytuj',
        'mark_done': '✔ Oznacz jako zrobione',
        'mark_pending': '↩ Oznacz jako do zrobienia',
        'delete': '🗑 Usuń',
        'add': 'Dodaj',
        'cancel': 'Anuluj',
        'error': 'Błąd',
        'invalid_date_title': 'Nieprawidłowa data',
        'add_student_title': 'Dodaj ucznia',
        'student_full_name': 'Imię i nazwisko ucznia:',
        'student_placeholder': 'np. Anna Kowalska',
        'new_assignment_title': 'Nowe zadanie – {name}',
        'edit_assignment_title': 'Edytuj zadanie',
        'title_required': 'Tytuł (wymagany):',
        'title_placeholder': 'np. Ćwiczenia z algebry, s. 45',
        'description_optional': 'Opis / uwagi (opcjonalnie):',
        'date_assigned': 'Data zadania:',
        'due_date': 'Termin:',
        'add_assignment_confirm': 'Dodaj zadanie',
        'save_changes': 'Zapisz zmiany',
        'delete_assignment_title': 'Usuń zadanie',
        'delete_assignment_confirm': 'Czy na pewno chcesz usunąć zadanie:\n"{title}"?',
        'remove_student_title': 'Usuń ucznia',
        'remove_student_confirm': 'Czy na pewno chcesz usunąć ucznia:\n"{name}"?\n\nWszystkie jego zadania również zostaną usunięte!',
        'select_date': 'Wybierz datę',
        'today': 'Dziś',
        'weekdays': 'Pn,Wt,Śr,Cz,Pt,So,Nd',
        'months': 'Styczeń,Luty,Marzec,Kwiecień,Maj,Czerwiec,Lipiec,Sierpień,Wrzesień,Październik,Listopad,Grudzień',
        'db_error_title': 'Błąd bazy danych',
        'err_empty_field': "Pole '{field}' nie może być puste.",
        'field_full_name': 'Imię i nazwisko',
        'field_title': 'Tytuł',
        'err_student_missing': "Uczeń o ID '{id}' nie istnieje.",
        'err_assignment_missing': "Zadanie o ID '{id}' nie istnieje.",
        'err_invalid_status': "Nieprawidłowy status: '{status}'. Dozwolone wartości: '{done}', '{pending}'.",
        'err_invalid_date': "Nieprawidłowa data '{value}'. Podaj poprawną datę w formacie RRRR-MM-DD.",
        'err_load': "Nie można wczytać bazy danych '{path}': {error}. Plik pozostał bez zmian. Przywróć lub napraw go przed ponownym uruchomieniem.",
        'err_invalid_db': "Nieprawidłowa baza danych '{path}': {error}. Plik pozostał bez zmian. Przywróć lub napraw go przed ponownym uruchomieniem.",
        'err_save': "Nie można zapisać bazy danych '{path}': {error}",
    },
}


def _load_language() -> str:
    try:
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            lang = json.load(f).get('language')
        if lang in LANGUAGES:
            return lang
    except (OSError, ValueError, AttributeError):
        pass
    return DEFAULT_LANGUAGE


_current = _load_language()


def get_language() -> str:
    return _current


def set_language(lang: str) -> None:
    global _current
    if lang not in LANGUAGES:
        return
    _current = lang
    try:
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump({'language': lang}, f)
    except OSError:
        pass


def t(key: str, **kwargs) -> str:
    text = _STRINGS[_current].get(key) or _STRINGS['en'].get(key, key)
    return text.format(**kwargs) if kwargs else text


def weekdays() -> list[str]:
    return t('weekdays').split(',')


def month_name(month: int) -> str:
    return t('months').split(',')[month - 1]
