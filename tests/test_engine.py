from pyquanttrade.engine.commands import backtest
from tests.policy_battery import test_policy_1

def test_backtest():
    backtest(test_policy_1,"AAPL", "2010-01-01", "2021-01-01")