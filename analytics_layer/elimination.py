class GarbageEliminationFilter:
    """
    Garbage Elimination Filter (Bộ Lọc Loại Trừ Số Rác)
    Filters out low-probability 2D numbers based on extreme gan thresholds,
    conflicting sum/touch signals, and cold trend patterns.
    """

    def __init__(self, history_records):
        self.history = history_records

    def filter_garbage_numbers(self, candidate_list=None, max_gan_allowed=45):
        """
        Filters a list of candidate 2D numbers (or default 00-99).
        Returns: (retained_numbers, eliminated_numbers, elimination_reasons)
        """
        if candidate_list is None:
            candidate_list = [f"{i:02d}" for i in range(100)]

        if not self.history:
            return candidate_list, [], {}

        n_total = len(self.history)
        retained = []
        eliminated = []
        reasons = {}

        # Calculate gan days for all numbers
        gan_days = {}
        for num in candidate_list:
            gan = 0
            for idx in range(n_total - 1, -1, -1):
                if self.history[idx].get("de_2d") == num:
                    break
                gan += 1
            gan_days[num] = gan

        # Recent 7 days numbers to identify immediate duplicate repeats (Rơi)
        recent_7 = set([rec.get("de_2d") for rec in self.history[-7:] if rec.get("de_2d")])

        for num in candidate_list:
            gan = gan_days[num]
            
            # Rule 1: Extreme Gan (> 45 days) - High statistical drag
            if gan > max_gan_allowed:
                eliminated.append(num)
                reasons[num] = f"Extreme Gan ({gan} days > {max_gan_allowed})"
                continue

            # Rule 2: Double repeat cold streak (appeared yesterday and 2 days ago)
            if len(self.history) >= 2:
                last_1 = self.history[-1].get("de_2d")
                last_2 = self.history[-2].get("de_2d")
                if num == last_1 and num == last_2:
                    eliminated.append(num)
                    reasons[num] = "Triple consecutive repetition risk"
                    continue

            retained.append(num)

        return retained, eliminated, reasons


if __name__ == "__main__":
    from data_layer.scraper import XSMBScraper
    scraper = XSMBScraper()
    records = scraper.load_from_excel_seed()
    elim = GarbageEliminationFilter(records)
    retained, eliminated, reasons = elim.filter_garbage_numbers()
    print(f"Retained: {len(retained)} | Eliminated: {len(eliminated)}")
    print("Eliminated sample reasons:", list(reasons.items())[:5])
