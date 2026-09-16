# Eghtesadino

Eghtesadino is a Python desktop application for personal financial management. It is designed to help students record everyday income and expenses, understand spending patterns, and work toward savings goals.

This defense copy was prepared in the context of the **Khwarizmi Youth Award** project.

## Features

- User registration and sign-in
- Income and expense tracking with categories and descriptions
- Dashboard with balance, income, expense, savings, goals, and recent transactions
- Savings goals with deadlines, progress tracking, and balance allocation
- Reports with spending summaries, category breakdowns, monthly comparisons, and trends
- Data-driven financial insights and budgeting recommendations
- Light and dark themes, display scaling, currency selection, privacy mode, and learning-tip settings

## Technology

- Python 3.10+
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the desktop interface
- SQLite 3 through Python's standard-library `sqlite3` module

## Project Status

This is a working competition project and remains under active development. The application is intended for local use and educational demonstration; it is not financial advice or a replacement for professional financial services.

## Installation and Run

Create a virtual environment, activate it, and install the dependency:

```bash
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .venv\Scripts\activate        # Windows
python -m pip install -r requirements.txt
python main.py
```

The application creates `financial_data.db` automatically in the application directory when it first starts. No database file is required in a fresh copy.

## Data and Privacy

Financial records are stored locally in SQLite. Display preferences, theme settings, and scaling preferences are stored in local JSON files. These runtime files are intentionally excluded from version control so personal data and machine-specific settings are not published.

## Project Structure

```text
main.py                 Application entry point and screen router
models/                 Database and financial-advisor logic
screens/                Login, dashboard, reports, goals, and settings screens
utils/                  Theme, colors, scaling, preferences, and shared UI helpers
requirements.txt        Runtime dependencies
```

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
