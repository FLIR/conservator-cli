from conservator.util import to_clean_string
from conservator.generated.schema import Query


class ConservatorStatsManager:
    def __init__(self, conservator):
        self.conservator = conservator

    def latest_n(self, n):
        return self.conservator.query(Query.last_nstats, number=n)

    def latest(self):
        return self.latest_n(1)[0]

    def __repr__(self):
        return f"<Statistics for {self.conservator}>"

    def __str__(self):
        s = f"{repr(self)}: \n"
        s += str(to_clean_string(self.latest()))
        return s
