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
