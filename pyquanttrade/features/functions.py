# -*- coding: utf-8 -*-
"""Functions from market data"""

__author__ = "Miguel Martin"
__version__ = "1"

import numpy as np


def days_to_constant(days, order=1):
    return float("%.3f" % (1 - pow(1 - 2 / (days + 1), 1 / order)))


def get_column(column):
    def return_function(data):
        return data[column]

    return return_function


def trailling(target="close", days=40, over_under="under"):
    def f():
        def g(x):
            return all(x[-1] > x[:-1])

        return g

    def return_function(data):
        column_name = "trailling_" + over_under + "_" + str(days) + "_of_" + target
        if column_name not in data.columns:
            data[column_name] = (
                data[target].rolling(window=days, min_periods=1).apply(f(), raw=True)
            )
        return data[column_name].copy()

    return return_function


def rolling_std(days, target="close"):
    def return_function(data):
        column_name = "rolling_std_" + str(days) + "_of_" + target
        if column_name not in data.columns:
            data[column_name] = data[target].rolling(days, min_periods=2).std()
        return data[column_name].copy()

    return return_function


def moving_average(days, target="close"):
    def return_function(data):
        column_name = "moving_average_" + str(days) + "_of_" + target
        if column_name not in data.columns:
            data[column_name] = data[target].rolling(days, min_periods=1).mean()
        return data[column_name].copy()

    return return_function


def weighted_moving_average(days, weights):
    def f(w):
        def g(x):
            return (w * x).sum() / sum(w)

        return g

    def return_function(data):
        if len(weights) == days:
            column_name = "weighted_moving_average_" + str(days)
            if column_name not in data.columns:
                data[column_name] = (
                    data["close"].rolling(window=days).apply(f(weights), raw=True)
                )
            return data[column_name].copy()
        else:
            raise Exception("Weights length and rolling mean must be same length")

    return return_function


def step_weighting_ma(days, first_weight=1, step=1):
    def f(w):
        def g(x):
            return (w * x).sum() / sum(w)

        return g

    def return_function(data):
        weights = np.linspace(first_weight, (days * step) + first_weight - step, days)
        column_name = "step_weighting_ma_" + str(days)
        if column_name not in data.columns:
            data[column_name] = (
                data["close"].rolling(window=days).apply(f(weights), raw=True)
            )
        return data[column_name].copy()

    return return_function


def percentage_weighting_ma(days, last_weight=1, step=0.5):
    def f(w):
        def g(x):
            return (w * x).sum() / sum(w)

        return g

    def return_function(data):
        weights = np.zeros(days)
        weights[-1] = last_weight
        for i in range(1, days):
            weights[-1 * (i + 1)] = weights[-1 * i] * step
        column_name = "percentage_weighting_ma_" + str(days)
        if column_name not in data.columns:
            data[column_name] = (
                data["close"].rolling(window=days).apply(f(weights), raw=True)
            )
        return data[column_name].copy()

    return return_function


def triangular_weighting_ma(days=10, shape="linear"):
    def f(w):
        def g(x):
            return (w * x).sum() / sum(w)

        return g

    def linear_triangular_weights():
        weights = np.zeros(days)
        weights[0 : int((days + 2) / 2) - 1] = range(1, int((days + 2) / 2))
        if days % 2 == 0:
            weights[int((days + 2) / 2) - 1 :] = range(1, int((days + 2) / 2))[::-1]
        else:
            weights[int((days + 2) / 2) - 1 :] = range(1, int((days + 2) / 2) + 1)[::-1]
        return weights

    def gaussian_triangular_weights():
        return 0

    if shape not in ["linear", "gaussian"]:
        raise Exception(type, " is not a type of triangular moving average")
    else:
        weight_options = {
            "linear": linear_triangular_weights,
            "gaussian": gaussian_triangular_weights,
        }
        weights_func = weight_options.get(shape)
        weights_values = weights_func()

    def return_function(data):
        column_name = str(shape) + "_trianguar_weighting_ma_" + str(days)
        if column_name not in data.columns:
            data[column_name] = (
                data["close"].rolling(window=days).apply(f(weights_values), raw=True)
            )
        return data[column_name].copy()

    return return_function


def pivot_point_weighting_ma(days):
    def f(w):
        def g(x):
            return (w * x).sum() / sum(w)

        return g

    def pivot_point_weights():
        weights = np.array(range(1, days + 1))
        weights = weights * 3 - days - 1
        return weights

    def return_function(data):
        weights = pivot_point_weights()
        column_name = "pivot_point_weighting_ma_" + str(days)
        if column_name not in data.columns:
            data[column_name] = (
                data["close"].rolling(window=days).apply(f(weights), raw=True)
            )
        return data[column_name].copy()

    return return_function


def geometric_moving_average(days):
    def return_function(data):
        column_name = "geometric_moving_average_" + str(days)
        if column_name not in data.columns:
            data[column_name] = pow(
                data["close"].rolling(window=days).apply(np.prod, raw=True), 1 / days
            )
        return data[column_name].copy()

    return return_function


def exponential_smoothing(constant, target="close"):
    def return_function(data):
        column_name = "exponential_smoothing_" + str(constant) + "%_of_" + target
        if column_name not in data.columns:
            data[column_name] = data[target].copy()
            for i in data[data[target].notnull()].index[1:]:
                # print(data[column_name].loc[:i])
                data.loc[i, column_name] = data[column_name].loc[:i][-2] + constant * (
                    data[target].loc[i] - data[column_name].loc[:i][-2]
                )
        return data[column_name].copy()

    return return_function


def second_order_exponential_smoothing(constant):
    def return_function(data):
        first_order = exponential_smoothing(constant)(data)
        column_name = "second_order_exponential_smoothing_" + str(constant) + "%"
        if column_name not in data.columns:
            data[column_name] = first_order.copy()
            for i in range(1, len(data["close"])):
                data[column_name].iloc[i] = data[column_name].iloc[i - 1] + constant * (
                    first_order.iloc[i] - data[column_name].iloc[i - 1]
                )
        return data[column_name].copy()

    return return_function


def third_order_exponential_smoothing(constant):
    def return_function(data):
        second_order = second_order_exponential_smoothing(constant)(data)
        column_name = "third_order_exponential_smoothing_" + str(constant) + "%"
        if column_name not in data.columns:
            data[column_name] = second_order.copy()
            for i in range(1, len(data["close"])):
                data[column_name].iloc[i] = data[column_name].iloc[i - 1] + constant * (
                    second_order.iloc[i] - data[column_name].iloc[i - 1]
                )
        return data[column_name].copy()

    return return_function


def lag_correction_exponential_smoothing(constant):
    def return_function(data):
        column_name = (
            "lag_correction_exponential_smoothing_" + str(constant * 100) + "%"
        )
        if column_name not in data.columns:
            first_order = exponential_smoothing(constant)(data)
            data[column_name] = data["close"] - first_order
            for i in range(1, len(data["close"])):
                data[column_name].iloc[i] = data[column_name].iloc[i - 1] + constant * (
                    data[column_name].iloc[i] - data[column_name].iloc[i - 1]
                )
            data[column_name] = data[column_name] + first_order
        return data[column_name].copy()

    return return_function


def double_moving_average(days):
    def return_function(data):
        column_name = "double_moving_average_" + str(days)
        if column_name not in data.columns:
            simple_ma = moving_average(days)(data)
            data[column_name] = simple_ma.rolling(days, min_periods=1).mean()
        return data[column_name].copy()

    return return_function


def double_smoothed_momentum(days1, days2):
    def return_function(data):
        column_name = "DSM" + str(days1) + "/" + str(days2)
        if column_name not in data.columns:
            momentum_val = momentum(days=days1)(data)
            constant = days_to_constant(days1)
            exp_smoothed = exponential_smoothing(constant, target=momentum_val.name)(
                data
            )
            constant = days_to_constant(days2, 2)
            data[column_name] = exponential_smoothing(
                constant, target=exp_smoothed.name
            )(data)
        return data[column_name].copy()

    return return_function


def regularized_exponential_ma(days, weight, target="close"):
    def return_function(data):
        column_name = "REMA_" + str(days) + "/" + str(weight) + "_of_" + str(target)
        if column_name not in data.columns:
            c = days_to_constant(days)
            data[column_name] = data[target].copy()
            for i in range(2, len(data)):
                data[column_name].iloc[i] = (
                    data[column_name].iloc[i - 1] * (1 + 2 * weight)
                    + c * (data[column_name].iloc[i] - data[column_name].iloc[i - 1])
                    - weight * data[column_name].iloc[i - 2]
                ) / (1 + weight)
        return data[column_name].copy()

    return return_function


def hull_moving_average(period=16, target="close"):
    def return_function(data):
        column_name = "hull_moving_average_" + str(period) + "_of_" + str(target)
        if column_name not in data.columns:
            period_ma = moving_average(period)(data)
            period2_ma = moving_average(int(period / 2))(data)
            data[column_name] = (
                (2 * period2_ma - period_ma)
                .rolling(int(pow(period, 1 / 2)), min_periods=1)
                .mean()
            )
        return data[column_name].copy()

    return return_function


def upper_keltner_channel(days=10):
    def return_function(data):
        column_name = "upper_keltner_" + str(days)
        if column_name not in data.columns:
            average_daily_price = (data["close"] + data["high"] + data["low"]) / 3
            if ("moving_average_" + str(days) + "_of_close") not in data.columns:
                moving_average(days)(data)
            data[column_name] = (
                data["moving_average_" + str(days) + "_of_close"] + average_daily_price
            )
        return data[column_name].copy()

    return return_function


def lower_keltner_channel(days=10):
    def return_function(data):
        column_name = "lower_keltner_" + str(days)
        if column_name not in data.columns:
            average_daily_price = (data["close"] + data["high"] + data["low"]) / 3
            if ("moving_average_" + str(days) + "_of_close") not in data.columns:
                moving_average(days)(data)
            data[column_name] = (
                data["moving_average_" + str(days) + "_of_close"] - average_daily_price
            )
        return data[column_name].copy()

    return return_function


def upper_percentage_band(c, band_target, center_target):
    def return_function(data):
        column_name = (
            "upper_percentage_band_"
            + str(c)
            + "_of_"
            + band_target.name
            + "_over_"
            + center_target.name
        )
        if column_name not in data.columns:
            print(center_target)
            data[column_name] = c * band_target + center_target.values
        return data[column_name].copy()

    return return_function


def lower_percentage_band(c, band_target, center_target):
    def return_function(data):
        column_name = (
            "lower_percentage_band_"
            + str(c)
            + "_of_"
            + band_target.name
            + "_under_"
            + center_target.name
        )
        if column_name not in data.columns:
            data[column_name] = -c * band_target + center_target.values
        return data[column_name].copy()

    return return_function


def upper_absolute_band(value, target):
    def return_function(data):
        column_name = "upper_absolute_band_" + str(value) + "_over_" + target.name
        if column_name not in data.columns:
            data[column_name] = value + target
        return data[column_name].copy()

    return return_function


def lower_absolute_band(value, target):
    def return_function(data):
        column_name = "lower_absolute_band_" + str(value) + "_under_" + target.name
        if column_name not in data.columns:
            data[column_name] = -value + target
        return data[column_name].copy()

    return return_function


def upper_bollinger_band(mean_days, std_days, c):
    def return_function(data):
        column_name = "upper_bollinger_band_" + str(mean_days) + "/" + str(std_days)
        if column_name not in data.columns:
            std_dev = rolling_std(std_days)(data)
            ma = moving_average(mean_days)(data)
            data[column_name] = ma + c * std_dev
        return data[column_name].copy()

    return return_function


def lower_bollinger_band(mean_days, std_days, c):
    def return_function(data):
        column_name = "lower_bollinger_band_" + str(mean_days) + "/" + str(std_days)
        if column_name not in data.columns:
            std_dev = rolling_std(std_days)(data)
            ma = moving_average(mean_days)(data)
            data[column_name] = ma - c * std_dev
        return data[column_name].copy()

    return return_function


def upper_volatility_band(c, dev_target, band_target, center_target):
    def return_function(data):
        if hasattr(band_target, "name") & hasattr(dev_target, "name"):
            column_name = (
                "upper_volatility_band_"
                + str(c)
                + "_times_"
                + band_target.name
                + "&"
                + dev_target.name
                + "_over_"
                + center_target.name
            )
        elif hasattr(band_target, "name"):
            column_name = (
                "upper_volatility_band_"
                + str(c)
                + "_times_"
                + band_target.name
                + "&"
                + str(dev_target)
                + "_over_"
                + center_target.name
            )
        else:
            column_name = (
                "upper_volatility_band_"
                + str(c)
                + "_times_"
                + str(band_target)
                + "&"
                + str(dev_target)
                + "_over_"
                + center_target.name
            )
        if column_name not in data.columns:
            data[column_name] = center_target + c * dev_target * band_target
        return data[column_name].copy()

    return return_function


def lower_volatility_band(c, dev_target, band_target, center_target):
    def return_function(data):
        if hasattr(band_target, "name") & hasattr(dev_target, "name"):
            column_name = (
                "lower_volatility_band_"
                + str(c)
                + "_times_"
                + band_target.name
                + "&"
                + dev_target.name
                + "_under_"
                + center_target.name
            )
        elif hasattr(band_target, "name"):
            column_name = (
                "lower_volatility_band_"
                + str(c)
                + "_times_"
                + band_target.name
                + "&"
                + str(dev_target)
                + "_under_"
                + center_target.name
            )
        else:
            column_name = (
                "lower_volatility_band_"
                + str(c)
                + "_times_"
                + str(band_target)
                + "&"
                + str(dev_target)
                + "_under_"
                + center_target.name
            )
        if column_name not in data.columns:
            data[column_name] = center_target - c * dev_target * band_target
        return data[column_name].copy()

    return return_function


def momentum(days=1, target="close"):
    def return_function(data):
        column_name = "momentum" + str(days) + "_of_" + str(target)
        if column_name not in data.columns:
            data[column_name] = data[target].diff(periods=days)
        return data[column_name].copy()

    return return_function


def momentum_percentage(days=1, target="close"):
    def return_function(data):
        column_name = "momentum_percentage" + str(days) + "_of_" + str(target)
        if column_name not in data.columns:
            data[column_name] = data[target].diff(periods=days)
            data.loc[days:, column_name] = data[column_name][days:].divide(
                data[target][: -1 * days].values
            )
        return data[column_name].copy()

    return return_function


def MACD_line(slow_trend, fast_trend, signal):
    def return_function(data):
        column_name = (
            "MACD_line_" + str(slow_trend) + "/" + str(fast_trend) + "/" + str(signal)
        )
        if column_name not in data.columns:
            slow_trend_data = exponential_smoothing(days_to_constant(slow_trend))(data)
            fast_trend_data = exponential_smoothing(days_to_constant(fast_trend))(data)
            data[column_name] = fast_trend_data - slow_trend_data
        return data[column_name].copy()

    return return_function


def MACD_signal(slow_trend, fast_trend, signal):
    def return_function(data):
        column_name = (
            "MACD_signal_" + str(slow_trend) + "/" + str(fast_trend) + "/" + str(signal)
        )
        if column_name not in data.columns:
            macd_line = MACD_line(slow_trend, fast_trend, signal)(data)
            data[column_name] = exponential_smoothing(
                days_to_constant(signal), target=macd_line.name
            )(data)
        return data[column_name].copy()

    return return_function


def MACD_histogram(slow_trend, fast_trend, signal):
    def return_function(data):
        column_name = (
            "MACD_histogram_"
            + str(slow_trend)
            + "/"
            + str(fast_trend)
            + "/"
            + str(signal)
        )
        if column_name not in data.columns:
            macd_line = MACD_line(slow_trend, fast_trend, signal)(data)
            macd_signal = MACD_signal(slow_trend, fast_trend, signal)(data)
            data[column_name] = macd_line - macd_signal
        return data[column_name].copy()

    return return_function


def divergence_index(slow_trend, fast_trend):
    def return_function(data):
        column_name = "divergence_index" + str(slow_trend) + "/" + str(fast_trend)
        if column_name not in data.columns:
            fast_trend_data = moving_average(fast_trend)(data)
            slow_trend_data = moving_average(slow_trend)(data)
            momentum_data = momentum()(data)
            data[column_name] = (fast_trend_data - slow_trend_data) / rolling_std(
                slow_trend, momentum_data.name
            )(data).pow(2)
        return data[column_name].copy()

    return return_function


def average_true_range(days=10, target="close"):
    def return_function(data):
        column_name = "average_true_range_" + str(days) + "_of_" + target
        high_col_name = "high" + target[5:]
        low_col_name = "low" + target[5:]
        if column_name not in data.columns:
            true_range = data[high_col_name] - data[low_col_name]
            data[column_name] = true_range.rolling(days, min_periods=1).mean()
        return data[column_name].copy()

    return return_function


def stochastic_percentageK(days):
    def f(x):
        lowest = x["low"].nsmallest(1)
        highest = x["high"].max()
        return 100 * (x["close"].iloc[-1] - lowest) / (highest - lowest)

    def return_function(data):
        column_name = "stochastic_percentageK_" + str(days)
        if column_name not in data.columns:
            data[column_name] = np.zeros(len(data))
            column_index = data.columns.get_loc(column_name)
            for i in range(len(data)):
                if i >= days - 1:
                    data.iloc[i, column_index] = f(
                        data.iloc[i - days + 1 : i + 1]
                    ).values
        return data[column_name].copy()

    return return_function


def stochastic_percentageD(days, daysK):
    def return_function(data):
        column_name_K = "stochastic_percentageK_" + str(daysK)
        column_name = "stochastic_percentageD_" + str(days) + "/" + str(daysK)
        if column_name not in data.columns:
            stochastic_percentageK(daysK)(data)
            data[column_name] = data[column_name_K].rolling(days).mean()
        return data[column_name].copy()

    return return_function


def ADoscillator():
    def f(x):
        buying_power = x["high"] - x["open"]
        selling_power = x["close"] - x["low"]
        DRF = (buying_power + selling_power) / 2 / (x["high"] - x["low"])
        return DRF

    def return_function(data):
        column_name = "A/D_oscillator"
        if column_name not in data.columns:
            data[column_name] = f(data)
        return data[column_name].copy()

    return return_function


def percentageR(days):
    def f(x):
        highest = x["high"].max()
        lowest = x["low"].min()
        buying_power = highest - x["close"].iloc[-1]
        return buying_power / (highest - lowest)

    def return_function(data):
        column_name = "percentageR_" + str(days)
        if column_name not in data.columns:
            data[column_name] = np.zeros(len(data))
            column_index = data.columns.get_loc(column_name)
            for i in range(len(data)):
                if i >= days - 1:
                    data.iloc[i, column_index] = f(data.iloc[i - days + 1 : i + 1])
        return data[column_name].copy()

    return return_function


def RSI(days):
    def f():
        def g(x):
            AU = x[x > 0].sum()
            AD = -x[x < 0].sum()
            if AD == 0:
                return 100
            else:
                RS = AU / AD
                return 100 - (100 / (1 + RS))

        return g

    def return_function(data):
        column_name = "RSI_" + str(days)
        if column_name not in data.columns:
            mom_name = momentum()(data).name
            data[column_name] = (
                data[mom_name].rolling(window=days).apply(f(), raw=False)
            )
        return data[column_name].copy()

    return return_function


def special_k():
    def return_function(data):
        column_name = "special_k"
        if column_name not in data.columns:
            momentum_days = [10, 15, 20, 30, 40, 65, 75, 100, 195, 265, 390, 530]
            moving_average_days = [10, 10, 10, 15, 50, 65, 75, 100, 130, 130, 130, 195]
            weighted_average_multiplier = [1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4]
            # Creating all the momentums and moving averages in advance
            ma_names = [
                moving_average(days=ma, target=momentum(days=mom)(data).name)(data).name
                for mom, ma in zip(momentum_days, moving_average_days)
            ]

            data[column_name] = 0
            column_name_pos = data.columns.get_loc(column_name)
            for i in range(0, len(data)):
                data.iloc[i, column_name_pos] = (
                    sum(
                        [
                            weight * data.iloc[i, data.columns.get_loc(ma_name)]
                            for ma_name, weight in zip(
                                ma_names, weighted_average_multiplier
                            )
                        ]
                    )
                    / 30
                )

        return data[column_name].copy()

    return return_function
