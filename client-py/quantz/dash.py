# Tracking 3 markets:
# Min, Max, and Avg
# Diff between min/max and avg should trade roughly in line.
# Any time they don't, we should arb.

# If diff between min/max < avg:
#   Buy min, sell max
# If diff between min/max > avg:
#   Sell min, buy max
