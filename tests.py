#!/usr/bin/env python
# encoding: utf-8
"""
tests.py

TODO: These tests need to be updated to support the Python 2.7 runtime

"""
import os
import unittest
import datetime
from stock import analyse, strategy


class AnalyseTestCase(unittest.TestCase):
    def setUp(self):
        self.start_date = datetime.datetime(2014, 5, 1)
        self.end_date = datetime.datetime(2014, 11, 13)
        self.symbols = ['SH600881', 'SH600064', 'SH600739',
                        'SH600219', 'SH600362', 'SH600028',
                        'SH601088', 'SH601989', 'SH600750',
                        'SH600298', 'SH601607']

    def test_backtest(self):
        print("backtest")
        s = strategy.TestStrategy()
        simulator = analyse.Simulator(self.symbols,
                                      s,
                                      self.start_date,
                                      self.end_date)
        tester = analyse.BackTester(100000)
        simulator.add_analyst('backtest', tester)
        simulator.run()
        simulator.analyse()
        result = simulator.report()
        print(result)
        self.assertIsNotNone(result)

    def test_eventprofile(self):
        print("event")
        s = strategy.TestStrategy()
        simulator = analyse.Simulator(self.symbols,
                                      s,
                                      self.start_date,
                                      self.end_date)
        event = analyse.EventProfiler()
        simulator.add_analyst('event', event)
        simulator.run()
        simulator.analyse()
        result = simulator.report()
        print(result)
        self.assertIsNotNone(result)
        
    def test_capm(self):
        print('capm')
        i = 0
        size = len(self.symbols)
        for symbol in self.symbols:
            i += 1
            print('{}:{}/{}'.format(symbol, i, size))
            x, y, beta, alpha = analyse.capm(symbol, 'SH999999',
                                             self.start_date,
                                             self.end_date)
            print(beta, alpha)
            self.assertIsNotNone(beta)
        
    def test_event(self):
        pass

    
if __name__ == '__main__':
    unittest.main()
