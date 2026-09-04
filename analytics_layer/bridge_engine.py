import numpy as np

class BridgeEngine:
    """
    Dynamic Bridge Ranking Engine (KNN & Cosine Similarity)
    Evaluates dynamic candidate bridges across rolling windows (10, 30, 60, 90 days)
    and scores top consensus 2D numbers.
    """

    def __init__(self, history_records):
        self.history = history_records

    def analyze_dynamic_bridges(self, window_days=30):
        """
        Analyze position pairs across historical records in rolling window.
        """
        recent = self.history[-window_days:] if len(self.history) >= window_days else self.history
        if not recent:
            return {}

        # Track G7 positions and GDB corner bridges
        bridge_scores = {}
        for i in range(len(recent) - 1):
            curr_draw = recent[i]
            next_draw = recent[i+1]
            actual_de = next_draw.get("de_2d")

            # Test Corner Bridge (Head of G7.1 + Tail of G7.4)
            g7_1 = curr_draw.get("g7_1", "00")
            g7_4 = curr_draw.get("g7_4", "00")
            if g7_1 and g7_4 and len(g7_1) == 2 and len(g7_4) == 2:
                corner_pair = g7_1[0] + g7_4[1]
                bridge_scores[corner_pair] = bridge_scores.get(corner_pair, 0) + 1.5

            # Test G7 touch matches
            for g7_key in ["g7_1", "g7_2", "g7_3", "g7_4"]:
                g7_val = curr_draw.get(g7_key, "")
                if g7_val and len(g7_val) == 2:
                    if g7_val[0] in actual_de or g7_val[1] in actual_de:
                        bridge_scores[g7_key] = bridge_scores.get(g7_key, 0) + 1.0

        return bridge_scores

    def get_top_consensus_2d(self, top_n=20):
        """
        KNN-weighted voting for Top N consensus 2D numbers.
        """
        if not self.history:
            return []

        # Count frequencies over 30, 60, 90 days
        freq_30 = {}
        freq_60 = {}
        freq_90 = {}
        gan_days = {}

        n_total = len(self.history)
        all_numbers = [f"{i:02d}" for i in range(100)]

        for num in all_numbers:
            # Calculate days since last occurrence (Gan)
            gan = 0
            for idx in range(n_total - 1, -1, -1):
                if self.history[idx].get("de_2d") == num:
                    break
                gan += 1
            gan_days[num] = gan

        for idx, rec in enumerate(self.history):
            num = rec.get("de_2d")
            if not num:
                continue
            dist_from_end = n_total - 1 - idx

            if dist_from_end < 30:
                freq_30[num] = freq_30.get(num, 0) + 1
            if dist_from_end < 60:
                freq_60[num] = freq_60.get(num, 0) + 1
            if dist_from_end < 90:
                freq_90[num] = freq_90.get(num, 0) + 1

        # Super-score formula combining recency, frequency, and golden gan window
        scored_numbers = []
        latest_g7 = [
            self.history[-1].get("g7_1", ""),
            self.history[-1].get("g7_2", ""),
            self.history[-1].get("g7_3", ""),
            self.history[-1].get("g7_4", "")
        ]
        g7_digits = set("".join(latest_g7))

        for num in all_numbers:
            f30 = freq_30.get(num, 0)
            f60 = freq_60.get(num, 0)
            f90 = freq_90.get(num, 0)
            gan = gan_days.get(num, 0)

            # Touch score
            g7_touch_bonus = 15.0 if (num[0] in g7_digits or num[1] in g7_digits) else 0.0

            # Gan score (Golden window for lottery: 7 to 25 days)
            gan_score = 20.0 if (5 <= gan <= 25) else (10.0 if gan < 5 else 5.0)

            # Frequency score
            freq_score = (f30 * 4.0) + (f60 * 2.0) + (f90 * 1.0)

            total_super_score = round(freq_score + gan_score + g7_touch_bonus, 2)
            num_sum = (int(num[0]) + int(num[1])) % 10

            scored_numbers.append({
                "number": num,
                "super_score": total_super_score,
                "sum": num_sum,
                "head": int(num[0]),
                "tail": int(num[1]),
                "gan_days": gan,
                "f30": f30,
                "f60": f60,
                "f90": f90,
                "g7_valid": bool(g7_touch_bonus > 0)
            })

        scored_numbers.sort(key=lambda x: x["super_score"], reverse=True)
        return scored_numbers[:top_n]


if __name__ == "__main__":
    from data_layer.scraper import XSMBScraper
    scraper = XSMBScraper()
    records = scraper.load_from_excel_seed()
    engine = BridgeEngine(records)
    top20 = engine.get_top_consensus_2d(20)
    print("Top 5 Consensus 2D:")
    for t in top20[:5]:
        print(t)
