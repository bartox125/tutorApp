from data_manager import DataManager
from app import HomeworkTrackerApp

def main() -> None:
    dm = DataManager()
    app = HomeworkTrackerApp(dm)
    app.mainloop()
if __name__ == '__main__':
    main()
