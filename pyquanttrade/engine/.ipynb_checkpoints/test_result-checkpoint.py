# -*- coding: utf-8 -*-
"""Functions from market data"""

__author__ = "Miguel Martin"
__version__ = "1"

import pandas as pd
import numpy as np


class TestResult:
    def __init__(self, data_sim):

        self.trade_list = None
        self.long_system_results = pd.DataFrame(index=data_sim.index)
        self.short_system_results = pd.DataFrame(index=data_sim.index)
        self.system_results = pd.DataFrame(index=data_sim.index)

        # init  long trades
        self.long_system_results["close"] = data_sim["close"]
        self.long_system_results["trade_close"] = np.NaN
        self.long_system_results["trade_sequence"] = np.NaN
        self.long_system_results["Daily_cumulative"] = 1.0
        self.long_system_results["Daily_sequence"] = 1.0

        # init  short trades
        self.short_system_results["close"] = data_sim["close"]
        self.short_system_results["trade_close"] = np.NaN
        self.short_system_results["trade_sequence"] = np.NaN
        self.short_system_results["Daily_cumulative"] = 1.0
        self.short_system_results["Daily_sequence"] = 1.0

        # init  All trades
        self.system_results["close"] = data_sim["close"]
        self.system_results["trade_close"] = np.NaN
        self.system_results["trade_sequence"] = np.NaN
        self.system_results["Daily_cumulative"] = 1.0
        self.system_results["Daily_sequence"] = 1.0

        # state vars
        self.last_closed_profit = {"long": 0.0, "short": 0.0, "all": 0.0}
        self.last_closed_inversion = {"long": 0.0, "short": 0.0, "all": 0.0}
        self._last_trades_len = {"long": 0.0, "short": 0.0, "all": 0.0}

    def _update(self, trade_type, i, row, trade_list, system_results):
        if trade_type == "all":
            trade_closed_len = (
                self._last_trades_len["long"] + self._last_trades_len["short"]
            )
        else:
            trade_closed_len = len(
                [
                    trade
                    for k, trade in trade_list.trades_closed.items()
                    if trade.type == trade_type
                ]
            )

        if trade_closed_len > self._last_trades_len[trade_type]:
            self._last_trades_len[trade_type] = trade_closed_len
            total_closed_profit = trade_list.get_close_profit(trade_type)
            delta_closed_profit = (
                total_closed_profit - self.last_closed_profit[trade_type]
            )
            self.last_closed_profit[trade_type] = total_closed_profit

            total_closed_inversion = trade_list.get_close_trades_total_open(trade_type)
            delta_closed_inversion = (
                total_closed_inversion - self.last_closed_inversion[trade_type]
            )
            self.last_closed_inversion[trade_type] = total_closed_inversion

            system_results.loc[i, ["trade_close"]] = (
                1 + (delta_closed_profit) / delta_closed_inversion
            )
            system_results.loc[i, ["trade_sequence"]] = (
                1 + (total_closed_profit) / total_closed_inversion
            )

        current_inversion = trade_list.get_current_total_open(trade_type)
        if current_inversion == 0:
            system_results.loc[i, ["Daily_sequence"]] = 1
        else:
            system_results.loc[i, ["Daily_sequence"]] = (
                1
                + (trade_list.get_current_profit(row["close"], trade_type))
                / current_inversion
            )

        if (
            len(
                [
                    trade
                    for k, trade in trade_list.trades_opened.items()
                    if trade.type == trade_type
                ]
            )
            > 0
        ):
            sum_open_price = trade_list.get_open_trades_total_open(trade_type)
            system_results.loc[i, ["Daily_cumulative"]] = (
                1
                + (
                    trade_list.get_current_profit(row["close"], trade_type)
                    - self.last_closed_profit[trade_type]
                )
                / sum_open_price
            )

    def update(self, i, row, trade_list):
        self.trade_list = trade_list
        self._update("long", i, row, trade_list, self.long_system_results)
        self._update("short", i, row, trade_list, self.short_system_results)
        self._update("all", i, row, trade_list, self.system_results)

    def describe(self):
        def max_drawdown(vec):
            maximums = np.maximum.accumulate(vec)
            drawdowns = 1 - vec / maximums
            return np.max(drawdowns)

        def safe_div(a, b):
            if b == 0:
                return 0
            return a / b

        def generate_system_stats(system_results):

            sim_years = system_results.shape[0] / 250
            global_results = [
                round(100 * (system_results["Daily_sequence"].tail(1)[0] - 1), 2)
            ]

            anual_net_profit_ratio = 100 * (
                (system_results["Daily_sequence"].tail(1)[0]) ** (1 / sim_years) - 1
            )
            global_results += [round(anual_net_profit_ratio, 2)]

            max_drawn_down = 100 * (max_drawdown(system_results["Daily_sequence"]))
            global_results += [round(max_drawn_down, 2)]

            if max_drawn_down == 0:
                ajusted_annual_return = 0.0
            else:
                ajusted_annual_return = 100 * (anual_net_profit_ratio / max_drawn_down)
            global_results += [round(ajusted_annual_return, 2)]

            return global_results

        idx = [
            "Net profit%",
            "Annual Return %",
            "Max DrawDown",
            "Risk Adjusted Return %",
        ]

        data = {
            "All trades": generate_system_stats(self.system_results),
            "Long trades": generate_system_stats(self.long_system_results),
            "Short trades": generate_system_stats(self.short_system_results),
        }

        global_statistics = pd.DataFrame(data, index=idx)

        # Trades statistics:

        # split long win, long lose, short win and short lose trades for further analysis.
        long_win_trades = [
            trade
            for k, trade in self.trade_list.trades_closed.items()
            if trade.profit >= 0
            if trade.type == "long"
        ]
        long_lose_trades = [
            trade
            for k, trade in self.trade_list.trades_closed.items()
            if trade.profit < 0
            if trade.type == "long"
        ]

        short_win_trades = [
            trade
            for k, trade in self.trade_list.trades_closed.items()
            if trade.profit >= 0
            if trade.type == "short"
        ]
        short_lose_trades = [
            trade
            for k, trade in self.trade_list.trades_closed.items()
            if trade.profit < 0
            if trade.type == "short"
        ]

        # Num of trades:
        len_long_trades = round(len(long_lose_trades) + len(long_win_trades), 0)
        len_short_trades = round(len(short_lose_trades) + len(short_win_trades), 0)
        len_all_trades = len_long_trades + len_short_trades

        all_trades = [len_all_trades]
        long_trades = [len_long_trades]
        short_trades = [len_short_trades]

        # Profit of Winners:
        profit_long_win_trades = round(
            np.sum([trade.profit for trade in long_win_trades]), 2
        )
        profit_short_win_trades = round(
            np.sum([trade.profit for trade in short_win_trades]), 2
        )
        profit_total_win_trades = profit_long_win_trades + profit_short_win_trades

        all_trades += [profit_total_win_trades]
        long_trades += [profit_long_win_trades]
        short_trades += [profit_short_win_trades]

        # Loss of Lossers:

        def safe_sum(l):
            if len(l) == 0:
                return 0
            return -np.sum(l)

        lose_long_lose_trades = round(
            safe_sum([trade.profit for trade in long_lose_trades]), 2
        )
        lose_short_lose_trades = round(
            safe_sum([trade.profit for trade in short_lose_trades]), 2
        )
        lose_total_lose_trades = lose_long_lose_trades + lose_short_lose_trades

        all_trades += [lose_total_lose_trades]
        long_trades += [lose_long_lose_trades]
        short_trades += [lose_short_lose_trades]

        # Net profit:
        net_long = profit_long_win_trades - lose_long_lose_trades
        net_short = profit_short_win_trades - lose_short_lose_trades
        net_total = net_long + net_short

        all_trades += [net_total]
        long_trades += [net_long]
        short_trades += [net_short]

        # Ratio Net profit:
        long_init_capital = np.sum(
            [
                trade.num_actions * trade.open_price
                for k, trade in self.trade_list.trades_closed.items()
                if trade.type == "long"
            ]
        )
        short_init_capital = np.sum(
            [
                trade.num_actions * trade.open_price
                for k, trade in self.trade_list.trades_closed.items()
                if trade.type == "short"
            ]
        )
        total_init_capital = long_init_capital + short_init_capital

        ratio_net_long = round(100 * safe_div(net_long, long_init_capital), 2)
        ratio_net_short = round(100 * safe_div(net_short, short_init_capital), 2)
        ratio_net_total = round(100 * safe_div(net_total, total_init_capital), 2)

        all_trades += [ratio_net_total]
        long_trades += [ratio_net_long]
        short_trades += [ratio_net_short]

        # Profit Factor:
        long_profit_factor = round(
            safe_div(profit_long_win_trades, lose_long_lose_trades), 2
        )
        short_profit_factor = round(
            safe_div(profit_short_win_trades, lose_short_lose_trades), 2
        )
        total_profi_factor = round(
            safe_div(profit_total_win_trades, lose_total_lose_trades), 2
        )

        all_trades += [total_profi_factor]
        long_trades += [long_profit_factor]
        short_trades += [short_profit_factor]

        # Percent Profitable:

        long_percent_profitable = round(
            safe_div(len(long_win_trades), len(long_win_trades + long_lose_trades)), 2
        )
        short_percent_profitable = round(
            safe_div(len(short_win_trades), len(short_win_trades + short_lose_trades)),
            2,
        )
        total_percent_profitable = round(
            safe_div(
                len(long_win_trades + short_win_trades),
                len(
                    long_win_trades
                    + short_win_trades
                    + long_lose_trades
                    + short_lose_trades
                ),
            ),
            2,
        )

        all_trades += [total_percent_profitable]
        long_trades += [long_percent_profitable]
        short_trades += [short_percent_profitable]

        # Payoff Ratio:

        long_avg_win = round(safe_div(profit_long_win_trades, len(long_win_trades)), 2)
        short_avg_win = round(
            safe_div(profit_short_win_trades, len(short_win_trades)), 2
        )
        total_avg_win = round(
            safe_div(profit_total_win_trades, len(long_win_trades + short_win_trades)),
            2,
        )

        long_avg_lose = round(safe_div(lose_long_lose_trades, len(long_lose_trades)))
        short_avg_lose = round(safe_div(lose_short_lose_trades, len(short_lose_trades)))
        total_avg_lose = round(
            safe_div(lose_total_lose_trades, len(long_lose_trades + short_lose_trades))
        )

        long_payoff_ratio = round(safe_div(long_avg_win, long_avg_lose), 2)
        short_payoff_ratio = round(safe_div(short_avg_win, short_avg_lose), 2)
        total_payoff_ratio = round(safe_div(total_avg_win, total_avg_lose), 2)

        all_trades += [total_payoff_ratio]
        long_trades += [long_payoff_ratio]
        short_trades += [short_payoff_ratio]

        # Maximum loss:
        def safe_min(l):
            if len(l) == 0:
                return 0
            return -np.min(l)

        long_max_loss = round(safe_min([trade.profit for trade in long_lose_trades]), 2)
        short_max_loss = round(
            safe_min([trade.profit for trade in short_lose_trades]), 2
        )
        total_max_loss = np.max([long_max_loss, short_max_loss])

        all_trades += [total_max_loss]
        long_trades += [long_max_loss]
        short_trades += [short_max_loss]

        # Maximum consecutive lossing trades:
        long_max_consecutives_lossing_trades = 0
        short_max_consecutives_lossing_trades = 0
        total_max_consecutives_lossing_trades = 0

        long_current_consecutives_lossing_trades = 0
        short_current_consecutives_lossing_trades = 0
        total_current_consecutives_lossing_trades = 0

        for k, trade in self.trade_list.trades_closed.items():
            if trade.type == "long" and trade.profit < 0:
                long_current_consecutives_lossing_trades += 1
                total_current_consecutives_lossing_trades += 1

            if trade.type == "short" and trade.profit < 0:
                short_current_consecutives_lossing_trades += 1
                total_current_consecutives_lossing_trades += 1

            if trade.type == "long" and trade.profit >= 0:
                if (
                    long_current_consecutives_lossing_trades
                    > long_max_consecutives_lossing_trades
                ):
                    long_max_consecutives_lossing_trades = (
                        long_current_consecutives_lossing_trades
                    )
                long_current_consecutives_lossing_trades = 0

                if (
                    total_current_consecutives_lossing_trades
                    > total_max_consecutives_lossing_trades
                ):
                    total_max_consecutives_lossing_trades = (
                        total_current_consecutives_lossing_trades
                    )
                total_current_consecutives_lossing_trades = 0

            if trade.type == "short" and trade.profit >= 0:
                if (
                    short_current_consecutives_lossing_trades
                    > short_max_consecutives_lossing_trades
                ):
                    short_max_consecutives_lossing_trades = (
                        short_current_consecutives_lossing_trades
                    )
                short_current_consecutives_lossing_trades = 0

                if (
                    total_current_consecutives_lossing_trades
                    > total_max_consecutives_lossing_trades
                ):
                    total_max_consecutives_lossing_trades = (
                        total_current_consecutives_lossing_trades
                    )
                total_current_consecutives_lossing_trades = 0

        if (
            long_current_consecutives_lossing_trades
            > long_max_consecutives_lossing_trades
        ):
            long_max_consecutives_lossing_trades = (
                long_current_consecutives_lossing_trades
            )

        if (
            short_current_consecutives_lossing_trades
            > short_max_consecutives_lossing_trades
        ):
            short_max_consecutives_lossing_trades = (
                short_current_consecutives_lossing_trades
            )

        if (
            total_current_consecutives_lossing_trades
            > total_max_consecutives_lossing_trades
        ):
            total_max_consecutives_lossing_trades = (
                total_current_consecutives_lossing_trades
            )

        all_trades += [total_max_consecutives_lossing_trades]
        long_trades += [long_max_consecutives_lossing_trades]
        short_trades += [short_max_consecutives_lossing_trades]

        idx = [
            "Num of trades",
            "Profit of Winners",
            "Loss of Lossers",
            "Net profit",
            "Ratio Net profit",
            "Profit Factor",
            "Percent Profitable",
            "Payoff Ratio",
            "Maximum loss",
            "Maximum consecutive lossing trades",
        ]

        data = {
            "All trades": all_trades,
            "Long trades": long_trades,
            "Short trades": short_trades,
        }

        all_trade_statistics = pd.DataFrame(data, index=idx)

        return global_statistics, all_trade_statistics
