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

def test_x():
    from pandas import DataFrame
    from pyquanttrade.features.functions import moving_average
    from pyquanttrade.features.indicators import cross_of_values
    from pyquanttrade.policy import Policy
    import traceback

    def test_all_in_one(stock_list, excel_name):
    
        start_date = '1999-01-01'
        end_date = '2022-01-01'

        fast_sma = 6
        slow_sma = 70

        class TraillingStopLoss(Policy):

            name = "TraillingStopLoss"
            version = "1.0"

            plot_functions = ['moving_average_50_of_close', 'hello']
            # stop loss parameters:
            long_stop_loss = 0.05
            short_stop_loss = 100
            long_stop_loss_trailling = True
            short_stop_loss_trailling = False

            def description(self):
                return "Estrategia de tipo moving average crossover. Inversión en largo cuando la SMA_10 supera SMA_40. Inversión en corto cuando la SMA_10 cae por debajo de SMA_40. Las posiciones corto/largo se cierran cuando se abren las contrarias."

            @classmethod
            def buy_long_when(self):
                func1 = moving_average(fast_sma)
                func2 = moving_average(slow_sma)
                return cross_of_values(func2, func1)

            @classmethod
            def close_long_when(self):
                func1 = moving_average(fast_sma)
                func2 = moving_average(slow_sma)
                return cross_of_values(func1, func2)
            pass

        policy_list = [TraillingStopLoss]

        combinations = policy_list
        number_of_combinations = len(combinations)

        results = list()
        for number,policy in enumerate(combinations):
            try:
                result = backtest(policy, stock_list, start_date, end_date, commission=0.01, slippage_perc=0.01, time_buffer=70)
                results.append(result[0])
                print(f'Backtest calculated: {number+1}/{number_of_combinations}')
            except:
                print(f'Error while processing {policy.name}')
                print(traceback.format_exc())


        combinations_name = [[policy.name] for policy in combinations]
        results_df = DataFrame(combinations_name, columns=['policy'])

        results_describe = [result.describe(True) for result in results]
        result_describe_one_table = [result.trades_stats['all'].append(result.system_stats['all'])['All trades'] for result in results_describe]
        results_df = results_df.join(DataFrame(result_describe_one_table, index=range(len(result_describe_one_table))))
        results_df.to_excel(excel_name, sheet_name='All trades')


    stock_list = ['XOM', 'GOOGL','FB']
    test_all_in_one(stock_list, 'results_all.xlsx')
    stock_list = ['SO', 'GOOGL', 'AAPL', 'MSFT', 'NEE', 'AMZN', 'V', 'AMT']
    test_all_in_one(stock_list, 'results_high_recovery_ratio.xlsx')