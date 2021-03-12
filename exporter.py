import time
import os
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server
from pytzstats.tzstats import Pytzstats

metrics = {
    "total_received": 'Lifetime total tokens received in transactions.',
    "total_sent": 'Lifetime total tokens sent in transactions.',
    "total_burned": 'Lifetime total tokens burned in tz.',
    "total_fees_paid": 'Lifetime fees paid in tz.',
    "total_rewards_earned": 'Lifetime rewards earned in tz.',
    "total_fees_earned": 'Lifetime fees earned in tz.',
    "total_lost": 'Lifetime fees earned in tz.',
    "frozen_deposits": "Currently frozen deposits",
    "frozen_rewards": "Currently frozen rewards.",
    "frozen_fees": "Currently frozen fees.",
    "unclaimed_balance": "Currently unclaimed balance (for vesting contracts and commitments).",
    "spendable_balance": "Currently spendable balance.",
    "total_balance": "Currently spendable and frozen balances (except frozen rewards).",
    "delegated_balance": "Current incoming delegations.",
    "staking_balance": "Current delegated and own total balance.",
    "total_delegations": "Lifetime count of delegations.",
    "active_delegations": "Currently active and non-zero delegations.",
    "blocks_baked": "Lifetime total blocks baked.",
    "blocks_missed": "Lifetime total block baking missed.",
    "blocks_stolen": "Lifetime total block baked at priority > 0.",
    "blocks_endorsed": "Lifetime total blocks endorsed.",
    "slots_endorsed": "Lifetime total endorsemnt slots endorsed.",
    "slots_missed": "Lifetime total endorsemnt slots missed.",
    "n_ops": "Lifetime total number of operations sent and received.",
    "n_ops_failed": "Lifetime total number of operations sent that failed.",
    "n_tx": "Lifetime total number of transactions sent and received.",
    "n_delegation": "Lifetime total number of delegations sent.",
    "n_origination": "Lifetime total number of originations sent.",
    "n_proposal": "Lifetime total number of proposals (operations) sent.",
    "n_ballot": "Lifetime total number of ballots sent."
}

class TzstatsCollector(object):
    def __init__(self, hashes=[]):
        self.client = Pytzstats()
        self.hashes = hashes
        self.gauges = {}
        for key in metrics.keys():
            self.gauges[key] = GaugeMetricFamily('tzstats_' + key, metrics[key], labels=['hash'])

    def collect(self):
        cache_keys = metrics.keys()
        for thash in self.hashes:
            data = self.client.get_account(thash)
            for key in data.keys():
                if key in cache_keys:
                    self.gauges[key].add_metric([thash], data[key])
                    yield self.gauges[key]

if __name__ == '__main__':
    hashes = os.getenv('hashes', ''.split(','))
    start_http_server(8000)
    REGISTRY.register(TzstatsCollector(hashes))
    while True:
        time.sleep(10)