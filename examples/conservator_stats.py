from conservator import Conservator, Credentials

conservator = Conservator(Credentials.default(), "https://flirconservator.com/graphql")
print(conservator.stats)

