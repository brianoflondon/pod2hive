from beem.market import Market


market = Market()

hive_usd = market.hive_usd_implied()
hive_btc = 1/market.hive_btc_ticker()
hive_HBD = market.ticker()['latest']

print(hive_usd)
print(hive_btc)

print(hive_HBD)

print(market.ticker())

