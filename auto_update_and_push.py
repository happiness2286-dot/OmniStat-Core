import os
import sys
import io
import datetime
import subprocess
import openpyxl

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from data_layer.scraper import XSMBScraper
from daily_runner import run_daily_pipeline

def update_excel_with_new_draw(excel_path, new_record):
    """
    Append new draw record to Excel sheet 'Du_Lieu_2026' if it's not already present.
    """
    if not os.path.exists(excel_path):
        print(f"[Excel Update Error] File not found: {excel_path}")
        return False

    wb = openpyxl.load_workbook(excel_path)
    if "Du_Lieu_2026" not in wb.sheetnames:
        print(f"[Excel Update Error] Sheet Du_Lieu_2026 not in workbook.")
        return False

    sheet = wb["Du_Lieu_2026"]
    
    # Check if date or GDB is already present in last row
    last_row = sheet.max_row
    last_date = str(sheet.cell(last_row, 2).value).strip() if last_row >= 2 else ""
    last_gdb = str(sheet.cell(last_row, 3).value).strip() if last_row >= 2 else ""

    new_date = str(new_record.get("date")).strip()
    new_gdb = str(new_record.get("gdb")).strip()

    if last_gdb == new_gdb or last_date == new_date:
        print(f"[Excel Update] Latest record ({new_date} - GDB {new_gdb}) is already present in Excel row {last_row}. Skipping duplicate append.")
        return False

    # Calculate new STT
    new_stt = (sheet.cell(last_row, 1).value or 0) + 1 if isinstance(sheet.cell(last_row, 1).value, int) else last_row

    new_row_idx = last_row + 1
    sheet.cell(new_row_idx, 1, new_stt)
    sheet.cell(new_row_idx, 2, new_date)
    sheet.cell(new_row_idx, 3, int(new_gdb) if new_gdb.isdigit() else new_gdb)
    sheet.cell(new_row_idx, 4, int(new_record["de_2d"]))
    sheet.cell(new_row_idx, 5, int(new_record["g7_1"]))
    sheet.cell(new_row_idx, 8, int(new_record["g7_2"]))
    sheet.cell(new_row_idx, 11, int(new_record["g7_3"]))
    sheet.cell(new_row_idx, 14, int(new_record["g7_4"]))

    wb.save(excel_path)
    print(f"✅ [Excel Update] Successfully appended new draw {new_date} (GDB {new_gdb}) to Excel row {new_row_idx}.")
    return True

def push_to_github():
    """
    Automated Git Commit & Push.
    """
    print("\n--- AUTOMATING GITHUB PUSH ---")
    try:
        # Check if git repository exists
        res = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True)
        if res.returncode != 0:
            print("[Git Info] Local directory is not initialized as Git repository. Initializing local git repo...")
            subprocess.run(["git", "init"], check=True)

        date_str = datetime.date.today().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"Auto-update XSMB data & quantitative models [{date_str}]"

        print("Executing: git add .")
        subprocess.run(["git", "add", "."], check=True)

        print(f"Executing: git commit -m '{commit_msg}'")
        commit_res = subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True, text=True)
        print(commit_res.stdout)

        # Check git remote
        remote_res = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True)
        if not remote_res.stdout.strip():
            print("⚠️ [Git Warning] No git remote 'origin' configured yet. Please configure remote URL via `git remote add origin <URL>`.")
            print(" local commit completed successfully!")
            return False

        print("Executing: git push")
        push_res = subprocess.run(["git", "push"], capture_output=True, text=True)
        print(push_res.stdout)
        if push_res.returncode == 0:
            print("🚀 [GitHub Success] Successfully pushed latest updates to GitHub!")
            return True
        else:
            print(f"⚠️ [Git Warning] Push returned error: {push_res.stderr}")
            return False
    except Exception as e:
        print(f"❌ [Git Error] Failed to execute git operations: {e}")
        return False

def auto_update_and_push_job():
    """
    Main job function:
    1. Fetches from mketqua.net.
    2. Updates Excel file.
    3. Runs quantitative pipeline & regenerates dashboard JSON.
    4. Commits & pushes changes to GitHub.
    """
    print("==================================================")
    print("⚡ OMNISTAT CORE: AUTOMATED FETCH & GITHUB PUSH")
    print("==================================================")

    scraper = XSMBScraper()
    live_data = scraper.fetch_from_mketqua()

    if not live_data:
        print("❌ Could not fetch data from mketqua.net")
        return

    excel_updated = update_excel_with_new_draw("Thong_Ke_G7_Va_Top20_XSMB_2026.xlsx", live_data)
    
    # Always re-run pipeline to ensure metrics & json are fresh
    run_daily_pipeline()

    # Commit & Push to GitHub
    push_to_github()
    print("==================================================")

if __name__ == "__main__":
    auto_update_and_push_job()
