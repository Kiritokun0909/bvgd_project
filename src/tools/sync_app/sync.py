import os
import subprocess
import datetime
import pandas as pd

# --- CONFIGURATION ---
EXCEL_PATH = r"C:\Users\hoduc\PycharmProjects\BVGD_Project\src\tools\sync_app\IpAddress.xlsx"
LOCAL_FOLDER = r"C:\Users\hoduc\PycharmProjects\BVGD_Project\dist"
REMOTE_SHARE = r"Users\Public\BackupFolder"
LOG_FOLDER = r"C:\Users\hoduc\PycharmProjects\BVGD_Project\src\tools\sync_app\logs"

USERNAME = "ADMIN"
PASSWORD = "123"

def sync_folders():
    # 1. Ensure log directory exists
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)

    # 2. Load Excel Data
    try:
        df = pd.read_excel(EXCEL_PATH)
        df.columns = df.columns.str.strip()
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    # 3. User Selection Logic
    groups = df['GroupName'].unique()
    print("Available Groups:", ", ".join(groups))
    choice = input("Enter 'All' to sync everything or enter a specific GroupName: ").strip().lower()

    if choice == 'all':
        targets = df
    else:
        targets = df[df['GroupName'].str.lower() == choice]
        if targets.empty:
            print(f"No match found for group: '{choice}'. Exiting.")
            return

    print(f"\nStarting deployment for {len(targets)} servers...\n")

    # 4. Processing Loop
    for index, row in targets.iterrows():
        ip = str(row['IpAddress']).strip()
        group = row['GroupName']

        destination = rf"\\{ip}\{REMOTE_SHARE}"
        date_str = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
        log_path = os.path.join(LOG_FOLDER, f"Sync_{group}_{ip}_{date_str}.txt")

        print("-" * 52)
        print(f"[{group}] Checking Connection to {ip}...")

        # Connection test
        ping_check = subprocess.run(["ping", "-n", "1", "-w", "1000", ip],
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)

        if ping_check.returncode == 0:
            print(f"[OK] {ip} is Online. Starting Sync...")

            try:
                subprocess.run(f'net use \\\\{ip}\\IPC$ /user:{USERNAME} {PASSWORD}', shell=True)

                # Run Robocopy
                result = subprocess.run(
                    ["robocopy", LOCAL_FOLDER, destination, "/E", f"/LOG:{log_path}", "/TEE"],
                    shell=True
                )

                if result.returncode <= 8:
                    print(f"[SUCCESS] {ip} Synced (Code: {result.returncode})")
                else:
                    print(f"[ERROR] Robocopy failed for {ip}. Check log.")

                subprocess.run(f'net use \\\\{ip}\\IPC$ /delete /y', shell=True)

            except Exception as e:
                print(f"[CRITICAL] Error: {e}")

        else:
            print(f"[SKIP] {ip} is Offline.")
            with open(log_path, "a") as log_file:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_file.write(f"{timestamp}: Machine was offline. Sync skipped.\n")

    print("\n--- All Selected Tasks Finished ---")


if __name__ == "__main__":
    sync_folders()