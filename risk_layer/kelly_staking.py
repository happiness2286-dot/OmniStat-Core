class KellyStakingEngine:
    """
    Fractional Kelly Criterion Staking Engine.
    Dynamically computes capital allocation and stake sizing based on Super-Score,
    frame stage (N1, N2, N3), and anomaly risk factors.
    """

    def __init__(self, base_bankroll=10000000): # 10,000,000 VND default bankroll
        self.bankroll = base_bankroll

    def calculate_stake(self, consensus_score, win_probability=0.55, frame_stage="N1", risk_level="LOW"):
        """
        Kelly Formula: f* = (b*p - q) / b
        where:
        b = odds ratio (e.g. 70 for 2D đề payout)
        p = estimated win probability
        q = 1 - p
        Fractional Kelly (Quarter / Half Kelly) is used for conservative capital preservation.
        """
        b = 70.0  # Standard odds multiplier for 2D đề
        p = min(max(win_probability, 0.1), 0.95)
        q = 1.0 - p

        raw_kelly = (b * p - q) / b
        raw_kelly = max(raw_kelly, 0.0)

        # Scale by fractional kelly (25% Kelly for risk control)
        fractional_kelly = raw_kelly * 0.25

        # Adjust multiplier based on frame stage
        stage_multipliers = {
            "N1": 1.0,
            "N2": 2.2,
            "N3": 4.8
        }
        stage_mult = stage_multipliers.get(frame_stage, 1.0)

        # Risk level reduction
        risk_reduction = 1.0
        if risk_level == "HIGH":
            risk_reduction = 0.5
        elif risk_level == "MEDIUM":
            risk_reduction = 0.8

        recommended_percent = min(fractional_kelly * stage_mult * risk_reduction, 0.15)
        recommended_stake = round(self.bankroll * recommended_percent, -3) # Round to nearest 1,000 VND

        return {
            "bankroll": self.bankroll,
            "frame_stage": frame_stage,
            "recommended_percent": round(recommended_percent * 100, 2),
            "recommended_stake_vnd": int(recommended_stake),
            "risk_level": risk_level
        }


if __name__ == "__main__":
    kelly = KellyStakingEngine()
    print("N1 Allocation:", kelly.calculate_stake(consensus_score=54.0, win_probability=0.55, frame_stage="N1"))
    print("N2 Allocation:", kelly.calculate_stake(consensus_score=54.0, win_probability=0.55, frame_stage="N2"))
