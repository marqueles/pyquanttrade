# -*- coding: utf-8 -*-

__author__ = "Miguel Martin"
__version__ = "1"

from pyquanttrade.market import marketData
import logging
import plotly.graph_objects as go

logger = logging.getLogger(__name__)


class Policy:
    long_stop_loss = 1
    short_stop_loss = 1
    long_stop_loss_trailling = False
    short_stop_loss_trailling = False

    ticker = "Hello"  # This remains so that the system does not break

    # def buy_when():

    # def sell_when():
    @staticmethod
    def sell_short_when():
        return lambda day, ticker, trades, data: False

    @staticmethod
    def buy_long_when():
        return lambda day, ticker, trades, data: False

    @staticmethod
    def close_short_when():
        return lambda day, ticker, trades, data: False

    @staticmethod
    def close_long_when():
        return lambda day, ticker, trades, data: False

    @classmethod
    def execute(cls, day, data, trades):
        actions = []

        f = cls.close_long_when()
        if f(day, cls.ticker, trades, data):
            actions += ["Close_long"]

        f = cls.close_short_when()
        if f(day, cls.ticker, trades, data):
            actions += ["Close_short"]

        f = cls.sell_short_when()
        if f(day, cls.ticker, trades, data):
            actions += ["Sell_short"]

        f = cls.buy_long_when()
        if f(day, cls.ticker, trades, data):
            actions += ["Buy_long"]

        return actions

    @classmethod
    def get_activity_list(cls, ticker, init_date, end_date):
        # get market data
        data = marketData.get_data(ticker, init_date, end_date)
        data["signals"] = None
        status = "none"
        trailling_point = 0
        # iter over date to check entries and exits.
        for data_tuple in data.iterrows():
            date = data_tuple[0]
            data_eod = data_tuple[1]
            # Get if is entry or exit and store as list
            actions = cls.execute(date, data, trades=None)

            record = []

            # Checking for status long
            if status == "long":
                if trailling_point < data_eod["close"]:
                    trailling_point = data_eod["close"]

                if "Close_long" in actions:
                    status = "none"
                    record.append("Close_long")
                elif "Buy_long" in actions:
                    record.append("Rebuy_long")
                else:
                    stop_loss_checker = (
                        entry_point - data_eod["close"]
                    ) / entry_point > cls.long_stop_loss
                    trailling_stop_loss_checker = (
                        trailling_point - data_eod["close"]
                    ) / trailling_point > cls.long_stop_loss_trailling
                    if stop_loss_checker or trailling_stop_loss_checker:
                        status = "none"
                        record.append("Close_long")

            elif status == "short":
                if trailling_point > data_eod["close"]:
                    trailling_point = data_eod["close"]

                if "Close_short" in actions:
                    status = "none"
                    record.append("Close_short")
                elif "Sell_short" in actions:
                    record.append("Resell_short")
                else:
                    stop_loss_checker = (
                        data_eod["close"] - entry_point
                    ) / entry_point > cls.long_stop_loss
                    trailling_stop_loss_checker = (
                        data_eod["close"] - trailling_point
                    ) / trailling_point > cls.long_stop_loss_trailling
                    if stop_loss_checker or trailling_stop_loss_checker:
                        status = "none"
                        record.append("Close_long")

            elif status == "none":
                if "Buy_long" in actions:
                    status = "long"
                    entry_point = data_eod["close"]
                    trailling_point = data_eod["close"]
                    record = "Buy_long"
                elif "Sell_short" in actions:
                    status = "short"
                    entry_point = data_eod["close"]
                    trailling_point = data_eod["close"]
                    record = "Buy_long"

            if record:
                data.loc[date, "signals"] = record
        return data




def plot_activity_list(activity_list):
    
    fig = go.Figure()

    #Decoding signal list as separate lists
    activity_list['buy_long'] = None
    activity_list.loc[activity_list['signals']=='Buy_long','buy_long'] = activity_list.loc[activity_list['signals']=='Buy_long','close']
    activity_list['rebuy_long'] = None
    activity_list.loc[activity_list['signals']=='Rebuy_long','rebuy_long'] = activity_list.loc[activity_list['signals']=='Rebuy_long','close']
    activity_list['close_long'] = None
    activity_list.loc[activity_list['signals']=='Close_long','close_long'] = activity_list.loc[activity_list['signals']=='Close_long','close']
    activity_list['sell_short'] = None
    activity_list.loc[activity_list['signals']=='Sell_short','sell_short'] = activity_list.loc[activity_list['signals']=='Sell_short','close']
    activity_list['resell_short'] = None
    activity_list.loc[activity_list['signals']=='Resell_short','resell_short'] = activity_list.loc[activity_list['signals']=='Resell_short','close']
    activity_list['close_short'] = None
    activity_list.loc[activity_list['signals']=='Close_short','close_short'] = activity_list.loc[activity_list['signals']=='Close_short','close']

    fig.add_trace(go.Scatter(x=activity_list['close'].index, y=activity_list['close'], mode='lines', name='Price', line={'width':1,'color':'black'}))
    if not activity_list['buy_long'].isnull().all(): 
        fig.add_trace(go.Scatter(x=activity_list['buy_long'].index, y=activity_list['buy_long'], mode='markers', name='Buy Long', marker ={'symbol':'arrow-up', 'size':9, 'color':'green'}))
    if not activity_list['rebuy_long'].isnull().all(): 
        fig.add_trace(go.Scatter(x=activity_list['rebuy_long'].index, y=activity_list['rebuy_long'], mode='markers', name='ReBuy Long', marker ={'symbol':'bowtie', 'size':9, 'color':'green'}))
    if not activity_list['close_long'].isnull().all(): 
        fig.add_trace(go.Scatter(x=activity_list['close_long'].index, y=activity_list['close_long'], mode='markers', name='Close Long', marker ={'symbol':'x', 'size':9, 'color':'green'}))
    if not activity_list['sell_short'].isnull().all(): 
        fig.add_trace(go.Scatter(x=activity_list['sell_short'].index, y=activity_list['sell_short'], mode='markers', name='Sell Short', marker ={'symbol':'arrow-down', 'size':9, 'color':'red'}))
    if not activity_list['resell_short'].isnull().all(): 
        fig.add_trace(go.Scatter(x=activity_list['resell_short'].index, y=activity_list['resell_short'], mode='markers', name='ReSell Short', marker ={'symbol':'bowtie-down', 'size':9, 'color':'red'}))
    if not activity_list['close_short'].isnull().all(): 
        fig.add_trace(go.Scatter(x=activity_list['close_short'].index, y=activity_list['close_short'], mode='markers', name='Close Short', marker ={'symbol':'x', 'size':9, 'color':'red'}))
    
    return fig

def build_policy(policy_dict):
    created_policy = type(policy_dict["name"], (Policy,), {})
    for attribute in policy_dict["policy"]["parameters"]:
        setattr(
            created_policy, attribute, policy_dict["policy"]["parameters"][attribute]
        )
    for function in policy_dict["policy"]["functions"]:
        function_definition = policy_dict["policy"]["functions"][function]
        setattr(
            created_policy, function, lambda: set_head_function(function_definition)
        )
    return created_policy


def set_head_function(function_definition):
    module_name = next(iter(function_definition))
    function_name = function_definition[module_name]
    params_definition = function_definition["params"]
    params = []
    head_function = getattr(globals()[module_name], function_name)
    for param in params_definition:
        if next(iter(param)) in ["functions", "indicators"]:
            params.append(set_head_function(param))
        else:
            params.append(next(iter(param.values())))
    return head_function(*params)
