from __future__ import annotations
import calendar
from datetime import date, timedelta
from typing import Callable, Optional
import customtkinter as ctk

_WEEKDAYS = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
_COLOR_TODAY_BG = '#1f538d'
_COLOR_SELECTED_BG = '#2ecc71'
_COLOR_HOVER = '#2b72b8'
_COLOR_NAV_BTN = ('gray80', 'gray25')
_COLOR_NAV_HOVER = ('gray70', 'gray35')
_COLOR_WEEKEND = ('#d35400', '#e67e22')
_COLOR_MUTED = ('gray60', 'gray45')

class DatePickerPopup(ctk.CTkToplevel):

    def __init__(self, parent, initial_date: Optional[date] = None, on_date_selected: Optional[Callable[[date], None]] = None, anchor_widget: Optional[ctk.CTkBaseClass] = None) -> None:
        super().__init__(parent)
        self._on_select = on_date_selected or (lambda d: None)
        self._today = date.today()
        self._selected: date = initial_date or self._today
        self._view_year: int = self._selected.year
        self._view_month: int = self._selected.month
        self.title('Select Date')
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.bind('<Escape>', lambda e: self.destroy())
        self._build_ui()
        self._populate_grid()
        self._position_window(parent, anchor_widget)

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        header = ctk.CTkFrame(self, fg_color='transparent')
        header.grid(row=0, column=0, padx=10, pady=(10, 4), sticky='ew')
        header.grid_columnconfigure(2, weight=1)
        ctk.CTkButton(header, text='«', width=26, height=26, corner_radius=5, fg_color=_COLOR_NAV_BTN, hover_color=_COLOR_NAV_HOVER, text_color=('gray10', 'gray90'), command=self._prev_year).grid(row=0, column=0, padx=(0, 2))
        ctk.CTkButton(header, text='‹', width=26, height=26, corner_radius=5, fg_color=_COLOR_NAV_BTN, hover_color=_COLOR_NAV_HOVER, text_color=('gray10', 'gray90'), command=self._prev_month).grid(row=0, column=1, padx=(0, 4))
        self._lbl_month_year = ctk.CTkLabel(header, text='', font=ctk.CTkFont(size=13, weight='bold'))
        self._lbl_month_year.grid(row=0, column=2, sticky='ew')
        ctk.CTkButton(header, text='›', width=26, height=26, corner_radius=5, fg_color=_COLOR_NAV_BTN, hover_color=_COLOR_NAV_HOVER, text_color=('gray10', 'gray90'), command=self._next_month).grid(row=0, column=3, padx=(4, 0))
        ctk.CTkButton(header, text='»', width=26, height=26, corner_radius=5, fg_color=_COLOR_NAV_BTN, hover_color=_COLOR_NAV_HOVER, text_color=('gray10', 'gray90'), command=self._next_year).grid(row=0, column=4, padx=(2, 0))
        weekday_frame = ctk.CTkFrame(self, fg_color='transparent')
        weekday_frame.grid(row=1, column=0, padx=10, pady=(2, 2), sticky='ew')
        for idx, day_name in enumerate(_WEEKDAYS):
            txt_color = _COLOR_WEEKEND if idx >= 5 else ('gray40', 'gray70')
            ctk.CTkLabel(weekday_frame, text=day_name, width=34, font=ctk.CTkFont(size=11, weight='bold'), text_color=txt_color).grid(row=0, column=idx, padx=1)
        self._grid_frame = ctk.CTkFrame(self, fg_color='transparent')
        self._grid_frame.grid(row=2, column=0, padx=10, pady=(0, 6), sticky='ew')
        footer = ctk.CTkFrame(self, fg_color='transparent')
        footer.grid(row=3, column=0, padx=10, pady=(4, 6), sticky='ew')
        footer.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(footer, text='Today', height=26, font=ctk.CTkFont(size=11), fg_color=_COLOR_NAV_BTN, hover_color=_COLOR_NAV_HOVER, text_color=('gray10', 'gray90'), command=self._pick_today).grid(row=0, column=0, padx=(0, 4), sticky='ew')
        ctk.CTkButton(footer, text='Cancel', height=26, font=ctk.CTkFont(size=11), fg_color=('gray75', 'gray40'), hover_color=('gray65', 'gray30'), text_color=('gray10', 'white'), command=self.destroy).grid(row=0, column=1, padx=(4, 0), sticky='ew')

    def _populate_grid(self) -> None:
        for widget in self._grid_frame.winfo_children():
            widget.destroy()
        month_name = calendar.month_name[self._view_month]
        self._lbl_month_year.configure(text=f'{month_name} {self._view_year}')
        cal = calendar.Calendar(firstweekday=0)
        weeks = cal.monthdatescalendar(self._view_year, self._view_month)
        while len(weeks) < 6:
            last_date = weeks[-1][-1]
            weeks.append([last_date + timedelta(days=i) for i in range(1, 8)])
        for row_idx, week in enumerate(weeks):
            for col_idx, d in enumerate(week):
                is_current_month = d.month == self._view_month
                is_selected = d == self._selected
                is_today = d == self._today
                is_weekend = col_idx >= 5
                if is_selected:
                    fg_color = _COLOR_SELECTED_BG
                    hover_color = '#27ae60'
                    text_color = 'white'
                    font_weight = 'bold'
                elif is_today:
                    fg_color = _COLOR_TODAY_BG
                    hover_color = _COLOR_HOVER
                    text_color = 'white'
                    font_weight = 'bold'
                else:
                    fg_color = 'transparent'
                    hover_color = ('gray85', 'gray30')
                    if not is_current_month:
                        text_color = _COLOR_MUTED
                    elif is_weekend:
                        text_color = _COLOR_WEEKEND
                    else:
                        text_color = ('gray10', 'gray90')
                    font_weight = 'normal'
                btn = ctk.CTkButton(self._grid_frame, text=str(d.day), width=34, height=26, corner_radius=5, fg_color=fg_color, hover_color=hover_color, text_color=text_color, font=ctk.CTkFont(size=11, weight=font_weight), command=lambda target_date=d: self._day_clicked(target_date))
                btn.grid(row=row_idx, column=col_idx, padx=1, pady=1)

    def _day_clicked(self, chosen_date: date) -> None:
        self._on_select(chosen_date)
        self.destroy()

    def _pick_today(self) -> None:
        self._day_clicked(self._today)

    def _prev_month(self) -> None:
        if self._view_month == 1:
            self._view_month = 12
            self._view_year -= 1
        else:
            self._view_month -= 1
        self._populate_grid()

    def _next_month(self) -> None:
        if self._view_month == 12:
            self._view_month = 1
            self._view_year += 1
        else:
            self._view_month += 1
        self._populate_grid()

    def _prev_year(self) -> None:
        self._view_year -= 1
        self._populate_grid()

    def _next_year(self) -> None:
        self._view_year += 1
        self._populate_grid()

    def _position_window(self, parent, anchor_widget: Optional[ctk.CTkBaseClass]) -> None:
        self.update_idletasks()
        width = max(308, self.winfo_reqwidth())
        height = self.winfo_reqheight()
        if anchor_widget is not None:
            anchor_widget.update_idletasks()
            root_x = anchor_widget.winfo_rootx()
            root_y = anchor_widget.winfo_rooty()
            widget_h = anchor_widget.winfo_height()
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            pos_x = root_x
            pos_y = root_y + widget_h + 4
            if pos_y + height > screen_h - 40:
                pos_y = root_y - height - 4
            if pos_x + width > screen_w:
                pos_x = max(10, screen_w - width - 10)
            self.geometry(f'{width}x{height}+{pos_x}+{pos_y}')
        else:
            parent.update_idletasks()
            px = parent.winfo_rootx() + parent.winfo_width() // 2 - width // 2
            py = parent.winfo_rooty() + parent.winfo_height() // 2 - height // 2
            self.geometry(f'{width}x{height}+{max(0, px)}+{max(0, py)}')

class DateInput(ctk.CTkFrame):

    def __init__(self, parent, initial_date: Optional[date] = None, on_change: Optional[Callable[[date], None]] = None, **kwargs) -> None:
        super().__init__(parent, fg_color='transparent', **kwargs)
        self._date: date = initial_date or date.today()
        self._on_change = on_change
        self.grid_columnconfigure(0, weight=1)
        self._container = ctk.CTkFrame(self, corner_radius=6, fg_color=('gray85', 'gray20'))
        self._container.grid(row=0, column=0, sticky='ew')
        self._container.grid_columnconfigure(0, weight=1)
        self._entry = ctk.CTkEntry(self._container, border_width=0, fg_color='transparent', font=ctk.CTkFont(size=12))
        self._entry.insert(0, self._date.isoformat())
        self._entry.grid(row=0, column=0, padx=(8, 0), pady=2, sticky='ew')
        self._entry.bind('<FocusOut>', self._on_entry_focus_out)
        self._entry.bind('<Return>', self._on_entry_focus_out)
        self._cal_btn = ctk.CTkButton(self._container, text='📅', width=32, height=28, corner_radius=5, fg_color='transparent', hover_color=('gray75', 'gray30'), text_color=('gray10', 'white'),font=ctk.CTkFont(size=14), command=self.open_picker)
        self._cal_btn.grid(row=0, column=1, padx=(2, 4), pady=2)

    def open_picker(self) -> None:
        current = self.get_date()
        DatePickerPopup(parent=self.winfo_toplevel(), initial_date=current, on_date_selected=self._set_date_from_picker, anchor_widget=self._container)

    def _set_date_from_picker(self, picked_date: date) -> None:
        self._date = picked_date
        self._entry.delete(0, 'end')
        self._entry.insert(0, picked_date.isoformat())
        if self._on_change:
            self._on_change(picked_date)

    def _on_entry_focus_out(self, event=None) -> None:
        raw_text = self._entry.get().strip()
        try:
            parsed = date.fromisoformat(raw_text)
            self._date = parsed
            if self._on_change:
                self._on_change(parsed)
        except ValueError:
            self._entry.delete(0, 'end')
            self._entry.insert(0, self._date.isoformat())

    def get_date(self) -> date:
        raw_text = self._entry.get().strip()
        try:
            return date.fromisoformat(raw_text)
        except ValueError:
            return self._date

    def set_date(self, new_date: date) -> None:
        self._date = new_date
        self._entry.delete(0, 'end')
        self._entry.insert(0, new_date.isoformat())
