#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from io import StringIO

import testcommon

import backtrader as bt


class BuyAndHold(bt.Strategy):
    def next(self):
        if len(self) == 1:
            self.buy(size=10)


def test_run(main=False):
    cases = [
        ([100, 100, 90, 100, 90], 1, 1),
        ([100, 100, 90, 100, 90, 80], 2, 2),
        ([100, 100, 90, 80, 100], 2, 0),
        ([100, 100, 90, 110, 100], 1, 1),
    ]
    for prices, max_length, current_length in cases:
        for fund in [False, True]:
            rows = ['2024-01-%02d,%s,%s,%s,%s,0,0' %
                    (i + 1, price, price, price, price)
                    for i, price in enumerate(prices)]
            data = bt.feeds.GenericCSVData(
                dataname=StringIO('\n'.join(rows)), name='prices',
                headers=False, dtformat='%Y-%m-%d')
            cerebro = bt.Cerebro(stdstats=False)
            cerebro.broker.setcash(1000)
            cerebro.adddata(data)
            cerebro.addstrategy(BuyAndHold)
            cerebro.addanalyzer(bt.analyzers.TimeDrawDown,
                                _name='timedd', fund=fund)
            cerebro.addanalyzer(bt.analyzers.DrawDown,
                                _name='drawdown', fund=fund)
            strat = cerebro.run()[0]
            timed = strat.analyzers.timedd
            regular = strat.analyzers.drawdown.get_analysis()
            analysis = timed.get_analysis()
            assert regular.max.len == max_length
            assert analysis['maxdrawdownperiod'] == max_length
            assert timed.ddlen == current_length
            assert timed.maxdd == regular.max.drawdown


if __name__ == '__main__':
    test_run(main=True)
