'''
models.py

This module defines the core data structures for the Smart Tracker application.
It contains blueprints for standard Expenses and recurring Subscriptions,
including data validation and calculation methods.
'''
import datetime as dt

class Expense:
    '''
    EXPENSE class: Represents a single financial transaction.

        Attributes:
            id (int): Unique Identifier
            name (str): Merchant/Product name
            amount (float): total expense (cannot be negative)
            category (str): general classfication (e.g., Food, Utilities)
            date (datetime): date of transaction
            tags (str): Specific, Custom labels for the transaction

    __init__ - initializes all the variables
    add_tag() - adds extra, specific custom tags to the Expense
    to_dict() - returns a dictionary with all the variables
    '''
    def __init__(self,id: int,name: str,amount: float,category: str,date: str,tags: set=None):
        self.id=id
        self.name=name

        # validating amount entered, non negative and numeric value
        try:
            self.amount=float(amount)
            if self.amount<0:
                raise ValueError("Amount cannot be negative.")
        except ValueError as e:
            raise ValueError(f"Invalid amount for {self.name}: {e}")

        self.category=category

        # validating date entered in the correct format YYYY-MM-DD
        try:
            self.date = dt.datetime.strptime(date, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid date format: {e}")

        # if no tags are provided, create an empty set. Otherwise, use the provided set
        self.tags=tags if tags is not None else set()

    def add_tag(self,new_tag: str):
        self.tags.add(new_tag.lower())

    def to_dict(self):
        return {
            "ID":self.id,
            "Name":self.name,
            "Amount":self.amount,
            "Category":self.category,
            "Date": self.date.strftime("%Y-%m-%d"),
            "Tags":", ".join(self.tags)
        }
    
class Subscription:
    '''
    SUBSCRIPTION: Represents a recurring financial subscription

    Attributes:
        id (int): Unique identifier
        name (str): Service provider
        cost (float): Amount charged per billing cycle
        billing_cycle (str): Frequency of charge ('monthly', 'weekly', 'yearly')
        next_billing_date (datetime): The upcoming billing date

    __init__            - initializes all the variables
    get_annual_cost()   - takes billing_cycle variable and 
                            calculates annual cost of the Subscription
    is_due_soon()       - subtracts the current date from the 
                            next billing date and runs an if statement 
                            to check if the due date is soon
    to_dict()           - returns a dictionary with all the variables
    '''
    def __init__(self, id: int, name: str, cost: float, billing_cycle: str, next_billing_date: str):
        self.id=id
        self.name=name
        
        # validating cost for non negative and numeric value
        try:
            self.cost=float(cost)
            if self.cost<0:
                raise ValueError("Cost cannot be negative")
        except ValueError as e:
            raise ValueError(f"Invalid cost for {self.name}: {e}")
        
        # validating the billing period, 
        # to only allow 'monthly', 'weekly', or 'yearly' as the valid input
        self.billing_cycle=billing_cycle.lower()
        if self.billing_cycle not in ['monthly', "weekly" ,"yearly"]:
            raise ValueError("Wrong Input. you can only enter: monthly, weekly or yearly")

        # validating date entered in the correct format YYYY-MM-DD
        try:
            self.next_billing_date=dt.datetime.strptime(next_billing_date, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid Date format: {e}")

    def get_annual_cost(self):
        if self.billing_cycle == "monthly":
            return self.cost*12
        elif self.billing_cycle == "weekly":
            return self.cost*52
        elif self.billing_cycle == "yearly":
            return self.cost
        else:
            return 0.0
        
    def to_dict(self):
        return {
            "ID": self.id,
            "Name": self.name,
            "Cost": self.cost,
            "Billing Cycle": self.billing_cycle,
            "Next billing date": dt.datetime.strftime(self.next_billing_date, "%Y-%m-%d"),
            "Annual Cost": self.get_annual_cost(),
        }