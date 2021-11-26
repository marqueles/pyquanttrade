# -*- coding: utf-8 -*-
"""Functions from market data"""

__author__ = "Miguel Martin"
__version__ = "1"

from market import marketData
from engine.trade import TradeList
from engine.test_result import TestResult
import pandas as pd
import numpy as np
from pydoc import locate
from datetime import datetime, timedelta
from queue import LifoQueue
from IPython.display import display, clear_output
import logging


def backtest(
    policy,
    tickers,
    start_at,
    stop_at,
    capital=10000,
    commision=0,
    slippage_perc=0,
    level=logging.WARNING,
):
    logging.basicConfig(level=level)
    if not isinstance(tickers, list):
        tickers = [tickers]

    trade_list = TradeList(level=level)
    time_buffer = 250
    first_day = (
        datetime.strptime(start_at, "%Y-%m-%d").date() - timedelta(days=time_buffer)
    ).isoformat()

    policies = {}
    data_sims = {}
    data_dict = {}
    policy_class = locate("policies.customPolicies." + policy + "." + policy)
    logging.info(policy_class)
    remaining_capital = capital
    for ticker in tickers:
        pol = policy_class(ticker)
        policies[ticker] = pol
        logging.info(pol.name)
        logging.info(pol.ticker)
        data = marketData.get_data(ticker, first_day, stop_at)
        data_sim = data.loc[data.index >= start_at]

        if not data_sims:
            result = TestResult(data_sim, ticker, capital)
        else:
            result.add_ticker(data_sim, ticker)

        data_sims[ticker] = data_sim
        data_dict[ticker] = data

    def calculate_num_shares(capital, share_price):
        num_shares = int(capital / share_price)
        remaining = capital - num_shares * share_price
        return (num_shares, remaining)

    def execute_policy(policy, i, row, data, capital):
        signals = policy.execute(str(i).split(" ")[0], data, trades=trade_list)
        ticker = policy.ticker
        remaining = capital
        for signal in signals:
            if signal == "Buy_long":

                logging.info(str(ticker) + " : " + str(i) + " -- " + signal)
                slip = slippage_perc * (row["high"] - row["low"])
                loss = policy_class.long_stop_loss
                trailling = policy_class.long_stop_loss_trailling
                shares, remaining = calculate_num_shares(remaining, row["open"])
                trade_list.open_trade(
                    ticker,
                    "long",
                    str(i),
                    row["open"],
                    shares,
                    loss,
                    trailling,
                    commision,
                    slip,
                )
                logging.info("num of shares buyed: " + str(shares))
                logging.info("cost of shares buyed: " + str(shares * row["open"]))

            if signal == "Close_long":

                logging.info(str(ticker) + " : " + str(i) + " -- " + signal)
                money = trade_list.close_open_trades(
                    ticker, "long", str(i), row["open"]
                )
                remaining += money

            if signal == "Sell_short":

                logging.info(str(ticker) + " : " + str(i) + " -- " + signal)
                slip = slippage_perc * (row["high"] - row["low"])
                loss = policy_class.short_stop_loss
                trailling = policy_class.short_stop_loss_trailling
                shares, remaining = calculate_num_shares(remaining, row["open"])
                trade_list.open_trade(
                    ticker,
                    "short",
                    str(i),
                    row["open"],
                    shares,
                    loss,
                    trailling,
                    commision,
                    slip,
                )

            if signal == "Close_short":

                logging.info(str(ticker) + " : " + str(i) + " -- " + signal)
                money = trade_list.close_open_trades(
                    ticker, "short", str(i), row["open"]
                )
                remaining += money
        return remaining

    for i, row in data_sims[tickers[0]].iterrows():
        for ticker in policies.keys():
            if data_sims[ticker].index.contains(i):
                remaining_capital = execute_policy(
                    policies[ticker],
                    i,
                    data_sims[ticker].loc[i],
                    data_dict[ticker],
                    remaining_capital,
                )

        money = trade_list.verify_stop_loss(str(i), row["low"], row["high"])
        remaining_capital += money

        result.update(i, row, trade_list)

    return result
