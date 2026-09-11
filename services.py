"""Business rules that coordinate models and database operations.

Keep checkout and return validation here rather than placing all logic in the menu.
"""

# Suggested checkout checks:
# 1. The member exists.
# 2. The equipment exists and is available.
# 3. The due date is valid.
# 4. Insert the loan and mark the equipment unavailable together.
