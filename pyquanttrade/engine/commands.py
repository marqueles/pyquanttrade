# -*- coding: utf-8 -*-
"""Functions from market data"""

# -*- coding: utf-8 -*-
"""Functions from market data"""

__author__ = "Miguel Martin"
__version__ = "1"

from pyquanttrade.market import marketData
from pyquanttrade.engine.trade import TradeList
from pyquanttrade.engine.test_result import TestResult
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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
    time_buffer=250,
):
    logging.basicConfig(level=level)
    if not isinstance(tickers, list):
        tickers = [tickers]

    trade_list = TradeList(level=level)
    first_day = (
        datetime.strptime(start_at, "%Y-%m-%d").date() - timedelta(days=time_buffer)
    ).isoformat()

    policies = {}
    data_sims = {}
    data_dict = {}
    policy_class = policy
    logging.info(policy_class)
    remaining_capital = {tick: capital for tick in tickers}
    for ticker in tickers:
        policies[ticker] = policy_class
        logging.info(policy_class.name)
        data = marketData.get_data_n_tries(ticker, first_day, stop_at, n_tries=5)
        data_sim = data.loc[data.index >= start_at]

        if not data_sims:
            result = TestResult(data_sim, ticker, capital)
        else:
            result.add_ticker(data_sim, ticker, capital)

        data_sims[ticker] = data_sim
        data_dict[ticker] = data

    def calculate_num_shares(capital, share_price):
        num_shares = int(capital / share_price)
        remaining = capital - num_shares * share_price
        return (num_shares, remaining)

    def execute_policy(policy, i, row, data, capital, ticker):
        last_day = data.iloc[data.index.get_loc(i) - 1]
        signals = policy.execute(
            str(last_day.name).split(" ")[0], data, trades=trade_list
        )
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
            ticker_row = data_sims[ticker].loc[i]
            if i in data_sims[ticker].index:
                remaining_capital[ticker] = execute_policy(
                    policies[ticker],
                    i,
                    ticker_row,
                    data_dict[ticker],
                    remaining_capital[ticker], 
                    ticker
                )

        for ticker in policies.keys():
            money = trade_list.verify_stop_loss(
                str(i), ticker_row["low"], ticker_row["high"]
            )
            remaining_capital[ticker] += money

            result.update(i, trade_list, ticker)

    return result
