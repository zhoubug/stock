import pandas as pd
import data
from model import Market
from redis import Redis
from rq_scheduler import Scheduler
import datetime

import zipline
from zipline.utils.factory import create_simulation_parameters


scheduler = Scheduler(connection=Redis())


def run_analyse(initialize, handle_data, codes, start, end):
    open_time = "09:30:00"
    close_time = "15:00:00"
    start_time = "{0} {1}".format(start, open_time)
    end_time = "{0} {1}".format(end, close_time)

    sim_params = create_simulation_parameters(
        start=pd.to_datetime(start_time).tz_localize("Asia/Shanghai").tz_convert("UTC"),
        end=pd.to_datetime(end_time).tz_localize("Asia/Shanghai").tz_convert("UTC"),
        data_frequency="daily",
        emission_rate="daily",
        sids=codes)

    zp_algo = zipline.TradingAlgorithm(initialize=initialize,
                                       handle_data=handle_data,
                                       namespace={},
                                       capital_base=10e6,
                                       sim_params=sim_params)

    d = Market.get_stocks(codes, start, end)
    d = {k: v.prices for k, v in d.iteritems()}
    d = pd.Panel(d)

    res = zp_algo.run(d)
    results = {}
    results['parameters'] = {}
    results['results'] = res
    return results

def update_data():
    now = datetime.datetime.now()
    if now.hour > 18:
        start = end = now.strftime("%Y-%m-%d")
    else:
        d = now - datetime.timedelta(days=1)
        start = end = d.strftime("%Y-%m-%d")
    data.update_h(start, end)
    data.update_hist(start, end)

def schedule(time, func):
    """
    avoid duplicated func
    """
    global scheduler
    for job in scheduler.get_jobs():
        if job.func == func:
            # already in scheduler
            return

    scheduler.schedule(
        scheduled_time=time,  # Time for first execution, in UTC timezone
        func=func,                     # Function to be queued
        args=[],
        interval=60*60*24,
    )


t = datetime.datetime.now()
time = t.replace(hour=22, minute=0)

schedule(time, update_data)
