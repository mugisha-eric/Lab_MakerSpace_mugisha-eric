"""Domain model classes for the MakerSpace system.

Implement Member, Equipment, and Loan with meaningful attributes and methods.
"""

class Member:
    def __init__(self, member_id, full_name, email, phone):
        self.member_id = member_id
        self.full_name = full_name
        self.email = email
        self.phone = phone

    def __str__(self):
        return f"Member({self.member_id}, {self.full_name}, {self.email}, {self.phone})"

class Equipment:
    def __init__(self, equipment_id, name, category, item_condition, is_available=True):
        self.equipment_id = equipment_id
        self.name = name
        self.category = category
        self.item_condition = item_condition
        self.is_available = is_available

    def __str__(self):
        return f"Equipment({self.equipment_id}, {self.name}, {self.category}, {self.item_condition}, Available: {self.is_available})"

class Loan:
    def __init__(self, loan_id, member_id, equipment_id, checkout_date, due_date, returned_date=None):
        self.loan_id = loan_id
        self.member_id = member_id
        self.equipment_id = equipment_id
        self.checkout_date = checkout_date
        self.due_date = due_date
        self.returned_date = returned_date

    def __str__(self):
        return f"Loan({self.loan_id}, Member ID: {self.member_id}, Equipment ID: {self.equipment_id}, Checkout: {self.checkout_date}, Due: {self.due_date}, Returned: {self.returned_date})"
