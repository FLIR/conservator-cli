from conservator.util import dict_to_clean_string


class ConservatorStats:
    def __init__(self, conservator):
        self.conservator = conservator

    def fetch_latest_n(self, n):
        return self.conservator.query("""
            query lastNStats($number: Int!) {
              lastNStats(number: $number) {
                id
                from
                to
                totalFileSize
                totalUserCount
                totalVideoCount
                totalDatasetCount
                totalImageCount
                totalDatasetCount
                totalDatasetAnnotations {
                  machineAnnotations {
                    total
                  }
                  humanAnnotations {
                    total
                  }

                }
              }
            }
            """, variables={"number": n})["lastNStats"]

    def __repr__(self):
        return f"<Statistics for {self.conservator}>"

    def __str__(self):
        result = self.fetch_latest_n(1)[0]
        s = f"{repr(self)}: \n"
        s += dict_to_clean_string(result, 1)
        return s
