import os
import sys
import io
import json
import datetime

# Fix Windows console encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from data_layer.scraper import XSMBScraper
from data_layer.data_validator import DataValidator
from analytics_layer.bridge_engine import BridgeEngine
from analytics_layer.markov_chain import MarkovChainEngine
from analytics_layer.elimination import GarbageEliminationFilter
from risk_layer.anomaly_detector import AnomalyDetector
from risk_layer.kelly_staking import KellyStakingEngine
from risk_layer.backtest_engine import BacktestEngine

def run_daily_pipeline(excel_path="Thong_Ke_G7_Va_Top20_XSMB_2026.xlsx", output_json="dashboard_data.json"):
    """
    Master Runner executing end-to-end quantitative analytics pipeline:
    1. Scrapes / loads XSMB historical & latest data.
    2. Validates data integrity.
    3. Runs Analytics Layer (Bridge KNN, Markov Transition, Garbage Elimination).
    4. Runs Risk Layer (Volatility Anomaly, Kelly Staking, Backtest Engine).
    5. Exports unified JSON dataset for both root & web_dashboard.
    """
    print("==================================================")
    print(" RUNNING OMNISTAT CORE QUANTITATIVE PIPELINE")
    print("==================================================")

    # 1. DATA LAYER
    scraper = XSMBScraper(excel_path)
    records = scraper.load_from_excel_seed()
    validator = DataValidator()

    valid_records = []
    for r in records:
        is_ok, _ = validator.validate_record(r)
        if is_ok:
            valid_records.append(r)

    print(f"[Data Layer] {len(valid_records)} valid historical draw records loaded.")

    # 2. ANALYTICS LAYER
    bridge_engine = BridgeEngine(valid_records)
    top20_consensus = bridge_engine.get_top_consensus_2d(20)
    top40_consensus = bridge_engine.get_top_consensus_2d(40)
    dynamic_bridges = bridge_engine.analyze_dynamic_bridges(30)

    markov_engine = MarkovChainEngine(valid_records)
    markov_preds = markov_engine.predict_next_state_probs()

    elim_filter = GarbageEliminationFilter(valid_records)
    retained_nums, eliminated_nums, elim_reasons = elim_filter.filter_garbage_numbers()

    print("[Analytics Layer] Bridge KNN, Markov Transition & Garbage Elimination completed.")

    # 3. RISK & FINANCIAL LAYER
    anomaly_detector = AnomalyDetector(valid_records)
    volatility_info = anomaly_detector.evaluate_draw_volatility()

    kelly_engine = KellyStakingEngine(10000000)
    staking_recommendation = kelly_engine.calculate_stake(
        consensus_score=top20_consensus[0]["super_score"] if top20_consensus else 50.0,
        win_probability=0.58,
        frame_stage="N1",
        risk_level=volatility_info["risk_level"]
    )

    backtester = BacktestEngine(valid_records)
    backtest_metrics = backtester.run_backtest(40)

    print("[Risk Layer] Volatility Detector, Kelly Staking & Backtest Engine completed.")

    # Generate 3D & 4D Predictions
    top_3d = []
    top_2d_nums = [t["number"] for t in top20_consensus[:5]]
    cand_cang = ["0", "2", "4", "5", "7"]
    for num in top_2d_nums:
        for c in cand_cang:
            top_3d.append({
                "cang": f"Càng {c}",
                "number_3d": f"{c}{num}",
                "base_2d": f"Đề {num}",
                "consensus_score": round(top20_consensus[0]["super_score"] * 0.9, 1),
                "classification": "MẠNH"
            })

    # 4. DASHBOARD JSON EXPORT (Save to root & web_dashboard)
    latest_draw = valid_records[-1] if valid_records else {}
    
    dashboard_data = {
        "metadata": {
            "system_name": "OmniStat Core Quantitative Engine",
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_records_analyzed": len(valid_records),
            "latest_draw": latest_draw
        },
        "analytics": {
            "top20_consensus": top20_consensus,
            "top40_consensus": top40_consensus,
            "dynamic_bridges": dynamic_bridges,
            "markov_predictions": markov_preds,
            "elimination_summary": {
                "retained_count": len(retained_nums),
                "eliminated_count": len(eliminated_nums),
                "eliminated_sample": list(elim_reasons.items())[:10]
            },
            "top_3d": top_3d[:20]
        },
        "risk_and_finance": {
            "volatility_info": volatility_info,
            "staking_recommendation": staking_recommendation,
            "backtest_metrics": backtest_metrics
        }
    }

    # Save to root directory
    with open("dashboard_data.json", "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)

    # Save to web_dashboard directory
    os.makedirs("web_dashboard", exist_ok=True)
    with open("web_dashboard/dashboard_data.json", "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)

    print(f"[Execution Layer] Successfully generated Web Dashboard JSON dataset -> dashboard_data.json")
    print("==================================================")
    return dashboard_data

if __name__ == "__main__":
    run_daily_pipeline()
