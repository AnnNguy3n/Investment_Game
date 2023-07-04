import pandas as pd
import numpy as np
import importlib.util
import os
from copy import deepcopy


def check_data(data_: pd.DataFrame):
    data = data_.reset_index(drop=True)

    # Check các trường bắt buộc
    required_cols = ["TIME", "PROFIT", "SYMBOL"]
    for col in required_cols:
        if col not in data.columns:
            raise Exception(f"Thiếu cột {col}")

    # Check kiểu dữ liệu của cột TIME và cột PROFIT
    if data["TIME"].dtype != "int64": raise
    if data["PROFIT"].dtype != "float64": raise

    # Check tính giảm dần của cột TIME
    if data["TIME"].diff().max() > 0:
        raise Exception("Các giá trị trong cột TIME phải được sắp xếp giảm dần")

    # Check các chu kì
    time_unique = data["TIME"].unique()
    for i in range(data["TIME"].max(), data["TIME"].min()-1, -1):
        if i not in time_unique:
            raise Exception(f"Thiếu chu kì {i}")

    return data


class Game:
    def __init__(self, data: pd.DataFrame, interest_rate: float, mode="human") -> None:
        self.__full = check_data(data)
        self.__IR = interest_rate
        self.__mode = mode
        self.__min = self.__full["TIME"].min()
        self.__max = self.__full["TIME"].max()

        self.__df_states = {}
        self.__df_profits = {}
        for cyc in range(self.__min, self.__max+1):
            syms = self.__full["SYMBOL"][self.__full["TIME"] == cyc]
            df = self.__full[self.__full["TIME"] <= cyc]
            df = df[df["SYMBOL"].isin(syms)].reset_index(drop=True)
            self.__df_profits[cyc] = df.loc[df["TIME"] == cyc, ["SYMBOL", "PROFIT"]].copy()
            df.loc[df["TIME"] == cyc, "PROFIT"] = 0.0
            self.__df_states[cyc] = df

        self.__cur_cyc = self.__min
        self.__acc_bal = 1e9
        self.__inv_his = {}
        self.__pro_his = {}

    def start_new_game(self):
        if self.__mode == "agent":
            raise Exception("Agent không được sử dụng phương thức này")

        self.__cur_cyc = self.__min
        self.__acc_bal = 1e9
        self.__inv_his = {}
        self.__pro_his = {}

    @property
    def interest_rate(self):
        return self.__IR

    @property
    def account_balance(self):
        return self.__acc_bal

    @property
    def data(self):
        return self.__df_states[self.__cur_cyc].copy()

    @property
    def investment_history(self):
        return deepcopy(self.__inv_his)

    @property
    def profit_history(self):
        return deepcopy(self.__pro_his)

    def __get_investment_result(self, inv_obj):
        if type(inv_obj) == list or type(inv_obj) == np.ndarray:
            if type(inv_obj) == list:
                inv_obj = np.array(inv_obj)

            if len(inv_obj) != len(self.__df_profits[self.__cur_cyc]):
                raise Exception("Độ dài array không bằng số công ty có thể đầu tư")

            if np.min(inv_obj) < 0.0:
                raise Exception("Tỉ lệ tiền khi đầu tư không được âm")

            _s = np.sum(inv_obj)
            if _s > 1.0:
                inv_obj /= _s

            inv_obj *= self.__df_profits[self.__cur_cyc]["PROFIT"]
            if _s < 1.0:
                new = np.zeros(inv_obj.shape[0]+1)
                new[:inv_obj.shape[0]] = inv_obj
                new[inv_obj.shape[0]] = (1.0-_s) * self.__IR
            else:
                new = inv_obj

            return new

        elif type(inv_obj) == dict:
            df_profit = self.__df_profits[self.__cur_cyc]
            temp_df = df_profit[df_profit["SYMBOL"].isin(inv_obj.keys())].reset_index(drop=True)
            temp_iv = {k:v for k,v in inv_obj.items() if k in temp_df["SYMBOL"].to_list()}
            list_value = list(temp_iv.values())
            if np.min(list_value) < 0.0:
                raise Exception("Tỉ lệ tiền khi đầu tư không được âm")

            _s = np.sum(list_value)
            if _s > 1.0:
                for key in temp_iv.keys():
                    temp_iv[key] /= _s

            for i in range(len(temp_df)):
                temp_iv[temp_df.iloc[i]["SYMBOL"]] *= temp_df.iloc[i]["PROFIT"]

            if _s < 1.0:
                temp_iv["NI"] = (1.0-_s) * self.__IR

            return temp_iv

    def invest(self, inv_obj, cycle):
        if self.__mode == "agent":
            raise Exception("Agent không được sử dụng phương thức này")

        if cycle != self.__cur_cyc:
            raise Exception("Chu kì đầu tư không đúng")

        if cycle > self.__max:
            raise Exception(f"Hiện chưa có chu kì {cycle}")

        result = self.__get_investment_result(inv_obj)
        if type(result) == dict:
            profit = np.sum(list(result.values()))
        elif type(result) == np.ndarray:
            profit = np.sum(result)

        self.__inv_his[cycle] = inv_obj
        self.__pro_his[cycle] = profit
        print("Overall profit:", profit)

        self.__acc_bal *= profit
        print("Account balance:", self.__acc_bal)

        self.__cur_cyc += 1

    def __load_agent(self, name):
        spec = importlib.util.spec_from_file_location("agent", f"Agents/{name}.py")
        agent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent)
        return agent.Agent(self.__full, self.__IR, "agent")

    def __load_agents(self):
        list_name = os.listdir("Agents/")
        self.__list_agent = []
        for name in list_name:
            if not name.startswith("__"):
                self.__list_agent.append(self.__load_agent(name.split(".")[0]))

    def run_agent_code(self):
        if self.__mode == "agent":
            raise Exception("Agent không được sử dụng phương thức này")

        try:
            self.__list_agent
        except:
            self.__load_agents()

        num_agent = len(self.__list_agent)
        self.__agn_acc_bal = [1e9] * num_agent
        self.__agn_inv_his = [{} for _ in range(num_agent)]
        self.__agn_pro_his = [{} for _ in range(num_agent)]

        old_value = self.__cur_cyc
        for cycle in range(self.__min, self.__max+1):
            self.__cur_cyc = cycle
            for i in range(num_agent):
                self.__list_agent[i]._Game__cur_cyc = cycle
                self.__list_agent[i]._Game__acc_bal = self.__agn_acc_bal[i]
                inv_obj = self.__list_agent[i].get_investment_object()
                self.__list_agent[i]._Game__inv_his[cycle] = inv_obj
                result = self.__get_investment_result(inv_obj)
                if type(result) == dict:
                    profit = np.sum(list(result.values()))
                elif type(result) == np.ndarray:
                    profit = np.sum(result)

                self.__list_agent[i]._Game__pro_his[cycle] = profit

                self.__agn_inv_his[i][cycle] = inv_obj
                self.__agn_pro_his[i][cycle] = profit
                self.__agn_acc_bal[i] *= profit

        self.__cur_cyc = old_value

    @property
    def agent_account_balance(self):
        if self.__mode == "agent":
            raise Exception("Agent không được sử dụng phương thức này")

        return deepcopy(self.__agn_acc_bal)

    @property
    def agent_investment_history(self):
        if self.__mode == "agent":
            raise Exception("Agent không được sử dụng phương thức này")

        return deepcopy(self.__agn_inv_his)

    @property
    def agent_profit_history(self):
        if self.__mode == "agent":
            raise Exception("Agent không được sử dụng phương thức này")

        return deepcopy(self.__agn_pro_his)
