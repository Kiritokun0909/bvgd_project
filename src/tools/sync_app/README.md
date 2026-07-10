This Python-based tool automates the process of mirroring a local distribution folder to multiple remote Virtual Machines (VMs) or servers over a local network. It includes connectivity checks (Ping), group-based targeting, and handles authenticated network shares.

## 📋 Features
* **Excel-based Target List:** Reads target IP addresses and group names from an `IpAddress.xlsx` file.
* **Group Selection:** Allows syncing to all machines or specific groups (e.g., specific departments or wards).
* **Connectivity Awareness:** Skips offline machines to save time.
* **Auto-Authentication:** Handles password-protected network shares using `net use`.
* **Robust Syncing:** Uses `Robocopy /E` to ensure the destination is updated with the source content.
* **Detailed Logging:** Generates individual timestamped logs for every machine.

Before running the script, you **must** update the configuration variables in `sync.py` to match your local environment.

1.  **Open `src/tools/sync_app/sync.py` in a text editor.**
2.  **Locate the `--- CONFIGURATION ---` section at the top.**
3.  **Update the following variables:**

    *   `EXCEL_PATH`: Absolute path to your `IpAddress.xlsx` file.
        *   *The Excel file must have columns: `GroupName` and `IpAddress`.*
    *   `LOCAL_FOLDER`: The absolute path of the **source folder** you want to copy (e.g., your build output or distribution folder).
    *   `REMOTE_SHARE`: The share name or path on the destination VMs.
    *   `LOG_FOLDER`: Directory where execution logs will be saved.
    *   `USERNAME`: Username for network share authentication.
    *   `PASSWORD`: Password for network share authentication.

## 📦 Prerequisites

* Python 3.x
* `pandas` and `openpyxl` libraries:
  ```bash
  pip install pandas openpyxl
  ```

## 🚀 Usage

### Manual Run
1. Open terminal/PowerShell.
2. Navigate to the project root.
3. Execute the script:
   ```bash
   python src/tools/sync_app/sync.py
   ```
4. **Choose Target:** When prompted, enter `All` to sync everything or type a specific `GroupName` (e.g., `KHAMBENH`).

### 📅 Scheduling (Every Sunday)

To automate this task for the hospital network, set it up in the 
Windows Task Scheduler **(taskschd.msc)**:
1. **Create the Task**

    Open **Task Scheduler** and click **Create Basic Task**.

    * Name: Weekly_App_Sync

    * Trigger: Select Weekly.

    * Day: Select Sunday.

    * Time: Set to a low-traffic time (e.g., 02:00 AM).


2. **Configure the Action**

    * Action: Start a program.

    * Program/script: **YOUR_PYTHON_EXE_PATH**, for example:  
    ```
        C:\Users\{YOUR_USERNAME}\PycharmProjects\{YOUR_PROJECT_NAME}\.venv\Scripts\python.exe
    ```

    * Add arguments:  **YOUR_PATH_TO_PYTHON_SCRIPT**, for example:
    ```
        C:\Users\{YOUR_USERNAME}\PycharmProjects\{YOUR_PROJECT_NAME}\src\tools\sync_app\sync.py
    ```
   
    * Reference: https://community.esri.com/t5/python-documents/schedule-a-python-script-using-windows-task/ta-p/915861



