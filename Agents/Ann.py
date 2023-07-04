import pandas as pd
import numpy as np
from game import Game


class Agent(Game):
    def __init__(self, data: pd.DataFrame, interest_rate: float, mode="agent") -> None:
        super().__init__(data, interest_rate, mode)
        self.name = "Ann"

    def get_investment_object(self):
        data = self.data
        all_syms = data["SYMBOL"][data["TIME"] == data["TIME"].max()]
        l_ = len(all_syms)
        syms = np.random.choice(all_syms, l_, replace=False)
        ratio = np.random.uniform(1.0, 1.0, l_)
        ratio /= np.sum(ratio)
        # ratio *= 0.8 # Để lại 20% số tiền để gửi ngân hàng
        dict_investment = {syms[i]:ratio[i] for i in range(l_)}
        return dict_investment # Trả ra dạng dictionary
        # Có thể trả ra dạng list hoặc ndarray
        # return ratio