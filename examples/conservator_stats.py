from conservator import Conservator, Credentials

credentials = Credentials.default()

conservator = Conservator(credentials)
print(conservator)
print(conservator.stats)

