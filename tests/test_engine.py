from pyquanttrade.engine.commands import backtest, backtest_and_visualise
from tests.policy_battery import test_policy_1
from tests.policy_battery import test_policy_2

def test_backtest():
    backtest(test_policy_2,"TSLA", "2012-01-01", "2021-01-01")

def test_backtest_and_visualise():
    backtest_and_visualise(test_policy_2,"TSLA", "2012-01-01", "2021-01-01")

def test_backest_multiple_stocks():
    stock_list = ['XOM','FB']
    result,_ = backtest(test_policy_2, stock_list, "1999-01-01", "2022-01-01")
    summary_result = result.describe(True)
    assert summary_result

def test_backtest_commission_slippage():
    def slippage(num_actions, open_price, close_price):
        return 0.01 * num_actions * (open_price + close_price)

    def commission(num_actions, open_price, close_price):
        return 0.01 * num_actions * (open_price + close_price)

    backtest(test_policy_2,"TSLA", "2012-01-01", "2021-01-01", commission=commission, slippage_perc=slippage)