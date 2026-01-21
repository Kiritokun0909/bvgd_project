# VM File Synchronization Tool

This PowerShell-based tool automates the process of mirroring a local distribution folder to multiple remote Virtual Machines (VMs) or servers over a local network. It includes connectivity checks (Ping) and handles authenticated network shares.

## 📋 Features
* **Multi-IP Support:** Reads target IP addresses from a central CSV file.
* **Connectivity Awareness:** Skips offline machines to save time.
* **Auto-Authentication:** Handles password-protected network shares using `net use`.
* **Robust Mirroring:** Uses `Robocopy /MIR` to ensure the destination is an exact replica of the source.
* **Detailed Logging:** Generates individual timestamped logs for every machine.

## ⚙️ Configuration

Before running the script, you **must** update the configuration variables in `SyncFolders.ps1` to match your local environment.

1.  **Open `SyncFolders.ps1` in a text editor.**
2.  **Locate the `--- CONFIGURATION ---` section at the top.**
3.  **Update the following variables:**

    *   `$ServerList`: Absolute path to your `IpAddress.csv` file.
        *   *Example:* `$ServerList = "C:\Scripts\SyncTool\IpAddress.csv"`
    *   `$LocalFolder`: The absolute path of the **source folder** you want to copy (e.g., your build output or distribution folder).
        *   *Example:* `$LocalFolder = "C:\Projects\MyApp\dist"`
    *   `$RemoteShare`: The share name or path on the destination VMs.
        *   *Example:* `$RemoteShare = "Users\Public\BackupFolder"`
    *   `$LogFolder`: Directory where execution logs will be saved. Ensure this path is valid or let the script create it.
        *   *Example:* `$LogFolder = "C:\Scripts\SyncTool\logs"`

### 🔐 Authentication (Optional)

If the destination shares are password-protected, you need to enable the authentication logic in the script:

1.  **Define Credentials:**
    Add your credentials at the top of the Configuration section:
    ```
    $User = "AdminUser"
    $Password = "YourStrongPassword"
    ```
2.  **Enable Authentication Logic:**
    Uncomment the following lines in `SyncFolders.ps1`:
    *   **Line 28:** `$NetPath = "\\$IP\IPC$"`
    *   **Line 29:** `net use $NetPath /user:$User $Password /persistent:no | Out-Null`
    *   **Line 43:** `net use $NetPath /delete /y | Out-Null`

## 🚀 Usage

### Manual Run
1. Open PowerShell as **Administrator**.
2. Navigate to the script directory.
3. Execute the script:
   ```
   powershell .\SyncFolders.ps1
   ```

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

    * Program/script: powershell.exe

    * Add arguments: ```powershell -ExecutionPolicy Bypass -File "C:\Scripts\SyncFolders.ps1"```




