"""SQLite connection, schema setup, and data-access helpers.

Use schema.sql as the reference design. Keep SQL operations parameterised.
"""

# Suggested responsibilities:
# - open a connection with foreign keys enabled
# - create tables on first launch
# - add, list, update, and search members/equipment
# - create and close loan records
# - provide report queries
