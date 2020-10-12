from conservator import Conservator, Config

conservator = Conservator(Config.default(), "https://flirconservator.com/graphql")
print(conservator.stats)

