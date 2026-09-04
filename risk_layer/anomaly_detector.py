import numpy as np

class AnomalyDetector:
    """
    Anomaly & Volatility Detector for OmniStat Core.
    Monitors market noise, abnormal gan clusters, and structural shifts.
    """

    def __init__(self, history_records):
        self.history = history_records

    def evaluate_draw_volatility(self, window_days=15):
        """
        Evaluate structural volatility over rolling window.
        Returns volatility status, risk level, and confidence index.
        """
        if len(self.history) < window_days:
            return {"status": "NORMAL", "risk_level": "LOW", "confidence": 0.85}

        recent = self.history[-window_days:]
        heads = [int(rec.get("head", 0)) for rec in recent]
        sums = [int(rec.get("sum", 0)) for rec in recent]

        std_head = np.std(heads)
        std_sum = np.std(sums)

        # High variance in heads/sums indicates volatile/noisy regime
        composite_volatility = (std_head + std_sum) / 2.0

        if composite_volatility > 3.2:
            status = "HIGH_NOISE"
            risk_level = "HIGH"
            confidence = 0.65
        elif composite_volatility > 2.7:
            status = "MODERATE"
            risk_level = "MEDIUM"
            confidence = 0.78
        else:
            status = "STABLE"
            risk_level = "LOW"
            confidence = 0.90

        return {
            "status": status,
            "risk_level": risk_level,
            "confidence": confidence,
            "composite_volatility": round(float(composite_volatility), 2),
            "std_head": round(float(std_head), 2),
            "std_sum": round(float(std_sum), 2)
        }


if __name__ == "__main__":
    from data_layer.scraper import XSMBScraper
    scraper = XSMBScraper()
    records = scraper.load_from_excel_seed()
    detector = AnomalyDetector(records)
    vol = detector.evaluate_draw_volatility()
    print("Market Volatility Analysis:", vol)
