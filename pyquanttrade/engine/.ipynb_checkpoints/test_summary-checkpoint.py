# -*- coding: utf-8 -*-
"""Functions from market data"""

__author__ = "Miguel Martin"
__version__ = "1"


class TestSummary:
    def __init__(self, system_desc, trades_desc, graphs):
        self.system_summary_table = system_desc
        self.trades_summary_table = trades_desc
        self.summary_graphs = graphs
