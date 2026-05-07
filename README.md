# python-project-sem-2

# 👻 GHOSTEX: Smart Financial Tracker & Analytics Engine

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-brightgreen)
![Pandas](https://img.shields.io/badge/Data-Pandas-150458?logo=pandas)
![NumPy](https://img.shields.io/badge/Math-NumPy-013243?logo=numpy)

**GHOSTEX** is a robust, desktop-based personal financial application engineered to move beyond basic data entry. It seamlessly tracks daily expenses and recurring subscriptions while utilizing a mathematical analytics engine to provide proactive financial intelligence.

[DASHBOARD]
https://i.ibb.co/pBL5vcxf/dashboard.png

[REPORT]
https://i.ibb.co/1tGhHrCp/report.png

## ✨ Key Features & "Smart" Capabilities

Unlike standard budget trackers, GHOSTEX actively analyzes your data:
- **🧠 Spending Anomaly Detection:** Utilizes NumPy to calculate the Mean and Standard Deviation of historical spending. It automatically flags mathematically unusual transactions (e.g., massive accidental charges) in a dedicated intelligence report.
- **⏳ Automated Billing Rollover:** An intelligent background engine that scans for past-due subscriptions upon boot and automatically pushes their next billing dates forward based on their specific cycle (Monthly, Weekly, Yearly).
- **🚨 Proactive Dashboard Alerts:** Calculates time-deltas to alert you of bills due within the next 3 days directly on the home screen.
- **📊 Pandas Aggregation Engine:** Groups spending by category and identifies top merchants instantly without slowing down the UI.
- **⚡ Real-Time State Synchronization:** Every addition or deletion triggers a backend data reload and a UI refresh, ensuring the Dashboard and Ledgers never display stale data.
- **🛡️ Validation Bouncers:** Strict pre-save logic that prevents duplicate IDs or malformed data from corrupting the local database.

## 🛠️ Technology Stack

- **Frontend:** Python `CustomTkinter` (Modern, Dark-Mode GUI)
- **Backend Analytics:** `Pandas`, `NumPy`
- **Data Persistence:** Python `csv` module (File handling)
- **Time/Math Logic:** Python `datetime` module

## 📂 Project Architecture

The application follows strict software engineering principles, separating the UI from the database and analytical logic:

* `main.py`: The entry point. Handles the CustomTkinter GUI, widgets, and real-time state management.
* `data_manager.py`: The database handler. Manages secure CSV reading/writing, row deletion, and the time-travel rollover engine.
* `analytics.py`: The "Brain". Uses Data Science libraries to process raw dictionaries, calculate standard deviations, and group category totals.
* `models.py`: Object-Oriented blueprints for `Expense` and `Subscription` objects, enforcing strict data validation upon instantiation.

## 🚀 Installation & Setup

Currently, GHOSTEX runs directly from the Python source code. Follow these steps to run it locally on your machine:

**1. Clone the repository**
```bash
git clone [https://github.com/YourUsername/GHOSTEX.git](https://github.com/YourUsername/GHOSTEX.git)
cd GHOSTEX
