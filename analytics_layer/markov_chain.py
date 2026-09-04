import numpy as np

class MarkovChainEngine:
    """
    Markov Chain Transition Model for 2D State Transitions.
    Calculates transition probability matrices for Heads (0-9), Tails (0-9), and Sums (0-9).
    """

    def __init__(self, history_records):
        self.history = history_records

    def build_transition_matrix(self, state_key="head"):
        """
        Build 10x10 transition probability matrix for state_key in ['head', 'tail', 'sum'].
        P[i, j] = P(State_t+1 = j | State_t = i)
        """
        matrix = np.zeros((10, 10), dtype=float)
        if len(self.history) < 2:
            return matrix

        for idx in range(len(self.history) - 1):
            curr_val = self.history[idx].get(state_key)
            next_val = self.history[idx + 1].get(state_key)

            if curr_val is not None and next_val is not None:
                i = int(curr_val)
                j = int(next_val)
                matrix[i, j] += 1.0

        # Normalize rows to probabilities
        row_sums = matrix.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        prob_matrix = matrix / row_sums

        return prob_matrix

    def predict_next_state_probs(self):
        """
        Predict probability distribution for next draw's Head, Tail, and Sum
        given the latest observed draw.
        """
        if not self.history:
            return {}, {}, {}

        latest = self.history[-1]
        latest_head = int(latest.get("head", 0))
        latest_tail = int(latest.get("tail", 0))
        latest_sum = int(latest.get("sum", 0))

        head_mat = self.build_transition_matrix("head")
        tail_mat = self.build_transition_matrix("tail")
        sum_mat = self.build_transition_matrix("sum")

        next_head_probs = {d: round(head_mat[latest_head, d], 4) for d in range(10)}
        next_tail_probs = {d: round(tail_mat[latest_tail, d], 4) for d in range(10)}
        next_sum_probs = {d: round(sum_mat[latest_sum, d], 4) for d in range(10)}

        # Rank Top 3 for Head, Tail, Sum
        top_heads = sorted(next_head_probs.items(), key=lambda x: x[1], reverse=True)[:3]
        top_tails = sorted(next_tail_probs.items(), key=lambda x: x[1], reverse=True)[:3]
        top_sums = sorted(next_sum_probs.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            "top_heads": top_heads,
            "top_tails": top_tails,
            "top_sums": top_sums,
            "full_head_probs": next_head_probs,
            "full_tail_probs": next_tail_probs,
            "full_sum_probs": next_sum_probs
        }


if __name__ == "__main__":
    from data_layer.scraper import XSMBScraper
    scraper = XSMBScraper()
    records = scraper.load_from_excel_seed()
    markov = MarkovChainEngine(records)
    res = markov.predict_next_state_probs()
    print("Markov Predictions:")
    print("Top 3 Heads:", res["top_heads"])
    print("Top 3 Tails:", res["top_tails"])
    print("Top 3 Sums:", res["top_sums"])
