import os
import sys
import pandas as pd

# Ensure root directory is in sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from data_layer.scraper import XSMBScraper
from risk_layer.backtest_engine import BacktestEngine

def run_detailed_verification():
    scraper = XSMBScraper()
    records = scraper.load_from_excel_seed()
    
    print(f"==================================================")
    print(f" OMNISTAT CORE: KIỂM CHỨNG TỶ LỆ TRÚNG LỊCH SỬ")
    print(f" Tổng số kỳ mở thưởng phân tích: {len(records)} kỳ")
    print(f"==================================================\n")
    
    backtester = BacktestEngine(records)
    res = backtester.run_backtest(top_n_predictions=40)
    
    print("📌 TỔNG HỢP CHỈ SỐ BACKTEST:")
    print(f" - Tổng số ngày kiểm thử: {res['total_days_tested']} ngày")
    print(f" - Số ngày trúng ngay N1: {res['n1_hits']} ngày")
    print(f" - Tỷ lệ trúng N1 (Ngày 1): {res['n1_win_rate']}%")
    print(f" - Tỷ lệ trúng N2 (Dồn tích): {res['n2_win_rate_estimate']}%")
    print(f" - Tỷ lệ trúng N3 (Trọn Khung K3N): {res['n3_win_rate_estimate']}%")
    print(f"\n📌 CHI TIẾT 15 NGÀY GẦN NHẤT:")
    
    summary = res.get("daily_results_summary", [])
    df = pd.DataFrame(summary)
    if not df.empty:
        df["hit_status"] = df["hit"].apply(lambda x: "✅ TRÚNG (HIT)" if x else "❌ XỊT (MISS)")
        print(df[["date", "actual_de", "hit_status"]].to_string(index=False))

if __name__ == "__main__":
    run_detailed_verification()
