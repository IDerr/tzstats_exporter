import time
import os
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server
from pytzstats.tzstats import Pytzstats

metrics = {
    "total_received": {
        "desc":'Lifetime total tokens received in transactions.',
        "labels": ['hash']
    },
    "total_sent": { 
        "desc": 'Lifetime total tokens sent in transactions.', 
        "labels": ['hash']
    },
    "total_burned": { 
        "desc": 'Lifetime total tokens burned in tz.', 
        "labels": ['hash']
    },
    "total_fees_paid": { 
        "desc": 'Lifetime fees paid in tz.', 
        "labels": ['hash']
    },
    "total_rewards_earned": { 
        "desc": 'Lifetime rewards earned in tz.', 
        "labels": ['hash']
    },
    "total_fees_earned": { 
        "desc": 'Lifetime fees earned in tz.', 
        "labels": ['hash']
    },
    "total_lost": { 
        "desc": 'Lifetime fees earned in tz.', 
        "labels": ['hash']
    },
    "frozen_deposits": { 
        "desc": "Currently frozen deposits", 
        "labels": ['hash']
    },
    "frozen_rewards": { 
        "desc": "Currently frozen rewards.", 
        "labels": ['hash']
    },
    "frozen_fees": { 
        "desc": "Currently frozen fees.", 
        "labels": ['hash']
    },
    "unclaimed_balance": { 
        "desc": "Currently unclaimed balance (for vesting contracts and commitments).", 
        "labels": ['hash']
    },
    "spendable_balance": { 
        "desc": "Currently spendable balance.", 
        "labels": ['hash']
    },
    "total_balance": { 
        "desc": "Currently spendable and frozen balances (except frozen rewards).", 
        "labels": ['hash']
    },
    "delegated_balance": { 
        "desc": "Current incoming delegations.", 
        "labels": ['hash']
    },
    "staking_balance": { 
        "desc": "Current delegated and own total balance.", 
        "labels": ['hash']
    },
    "total_delegations": { 
        "desc": "Lifetime count of delegations.", 
        "labels": ['hash']
    },
    "active_delegations": { 
        "desc": "Currently active and non-zero delegations.", 
        "labels": ['hash']
    },
    "blocks_baked": { 
        "desc": "Lifetime total blocks baked.", 
        "labels": ['hash']
    },
    "blocks_missed": { 
        "desc": "Lifetime total block baking missed.", 
        "labels": ['hash']
    },
    "blocks_stolen": { 
        "desc": "Lifetime total block baked at priority > 0.", 
        "labels": ['hash']
    },
    "blocks_endorsed": { 
        "desc": "Lifetime total blocks endorsed.", 
        "labels": ['hash']
    },
    "slots_endorsed": { 
        "desc": "Lifetime total endorsemnt slots endorsed.", 
        "labels": ['hash']
    },
    "slots_missed": { 
        "desc": "Lifetime total endorsemnt slots missed.", 
        "labels": ['hash']
    },
    "n_ops": { 
        "desc": "Lifetime total number of operations sent and received.", 
        "labels": ['hash']
    },
    "n_ops_failed": { 
        "desc": "Lifetime total number of operations sent that failed.", 
        "labels": ['hash']
    },
    "n_tx": { 
        "desc": "Lifetime total number of transactions sent and received.", 
        "labels": ['hash']
    },
    "n_delegation": { 
        "desc": "Lifetime total number of delegations sent.", 
        "labels": ['hash']
    },
    "n_origination": { 
        "desc": "Lifetime total number of originations sent.", 
        "labels": ['hash']
    },
    "n_proposal": { 
        "desc": "Lifetime total number of proposals (operations) sent.", 
        "labels": ['hash']
    },
    "n_ballot": { 
        "desc": "Lifetime total number of ballots sent.", 
        "labels": ['hash']
    },
}

explorer_metrics = {
    "cycle": { 
        "desc": "Current cycle", 
        "labels": ['network']
    },
}

customs_metrics = {
    "next_endorsing": { 
        "desc": "Next endorsing time (in minutes)", 
        "labels": ['network']
    },
}

class TzstatsCollector(object):
    def __init__(self, hashes=[]):
        self.network = "main"
        self.client = Pytzstats()
        self.hashes = hashes
        self.gauges = {}
        for key in metrics.keys():
            self.gauges[key] = GaugeMetricFamily('tzstats_' + key, metrics[key]["desc"], labels=metrics[key]["labels"].append("network"))
        for key in explorer_metrics.keys():
            self.gauges[key] = GaugeMetricFamily('tzstats_' + key, explorer_metrics[key]["desc"], labels=explorer_metrics[key]["labels"])
        self.gauges["tzstats_next_endorsing"] = GaugeMetricFamily("tzstats_next_endorsing", explorer_metrics[key]["desc"], labels=explorer_metrics[key]["labels"])
        self.gauges["tzstats_next_baking"] = GaugeMetricFamily("tzstats_next_baking", explorer_metrics[key]["desc"], labels=explorer_metrics[key]["labels"])


    def collect(self):
        cache_keys = metrics.keys()
        cache_explorer_metrics = explorer_metrics.keys()
        explorer_data = self.client.get_explorer_tip()
        for thash in self.hashes:
            data = self.client.get_account(thash)
            for key in data.keys():
                if key in cache_keys:
                    self.gauges[key].add_metric([thash, self.network], data[key])
                    yield self.gauges[key]
            if data.get("next_endorse_height", None) is not None:
                self.gauges["tzstats_next_endorsing"].add_metric([thash, self.network], data["next_endorse_height"] - explorer_data["height"])
                yield self.gauges["tzstats_next_endorsing"]
                self.gauges["tzstats_next_baking"].add_metric([thash, self.network], data["next_bake_height"] - explorer_data["height"])
                yield self.gauges["tzstats_next_baking"]
        
        for key in explorer_data.keys():
            if key in cache_explorer_metrics:
                self.gauges[key].add_metric([self.network], explorer_data[key])
                yield self.gauges[key]
        
if __name__ == '__main__':
    hashes = os.getenv('HASHES', '').split(',')
    start_http_server(8000)
    REGISTRY.register(TzstatsCollector(hashes))
    while True:
        time.sleep(10)