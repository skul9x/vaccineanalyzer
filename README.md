# Vaccine Management Assistant

A PySide6-based desktop application for managing and analyzing vaccine schedules. This application integrates with VNCDC data to search for patients, analyze their vaccination history, identify missing vaccines, and help schedule appointments via HIS (Hospital Information System) integration.

## Features

-   **Patient Search:** Search for patients by phone number using VNCDC data.
-   **Vaccination Analysis:**
    -   **Administered List:** View history of administered vaccines with doses and dates.
    -   **Action Plan:** Automatically identifies missing vaccines based on age and history ("KẾ HOẠCH & DỰ BÁO").
    -   **Status Indicators:** Visual tags for Due, Warning, Info, etc.
-   **HIS Integration:**
    -   Match VNCDC patient data with HIS records (Name, DOB, Phone).
    -   Schedule appointments directly to HIS (F10).
-   **Export Tools:**
    -   Generate images for "Vaccinated" and "Missing" lists to share with patients.
-   **Vaccine Data:**
    -   Auto-update vaccine list from VNCDC.
    -   Tooltip support for long vaccine descriptions.

## Tech Stack

-   **Language:** Python 3.x
-   **GUI Framework:** PySide6 (Qt for Python)
-   **Icons:** QtAwesome (FontAwesome 5)
-   **Networking:** Requests (for data fetching)
-   **Database:** (Internal usage for caching/logic)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_folder>
    ```

2.  **Install dependencies:**
    ```bash
    pip install PySide6 qtawesome requests
    ```
    *(Note: Check for any other specific dependencies in the source code if `requirements.txt` is missing)*

3.  **Run the application:**
    ```bash
    python main_pyside.py
    ```

## Usage

1.  **Login:** Enter your credentials (if required) in the Config tab.
2.  **Search:** Go to the "Analysis" tab, enter a phone number, and press Enter.
3.  **Analyze:** Select a patient from the results. The app will fetch history and display:
    -   **Left Column:** Patient Info & HIS Status.
    -   **Middle Column:** History of administered vaccines.
    -   **Right Column:** Predicted missing vaccines/Action plan.
4.  **Schedule:** Press `F10` or click "Đặt Hẹn" to schedule for the matched HIS patient.
5.  **Export:** Use the image icons to export lists as images.

## Structure

-   `main_pyside.py`: Application entry point.
-   `app_controller.py`: Main application controller orchestrating services and UI.
-   `controllers/`: Logic for specific tabs/features.
-   `ui_pyside/`: UI components (Views).
-   `services/`: Backend logic (Analysis, Data Formatting, Image Export, Worker).
-   `live_worker/`: Background worker for data fetching.

## License

[Proprietary/Internal Use]
