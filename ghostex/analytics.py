"""
analytics.py

This module serves as the analytical engine (the "Brain") of the Smart Tracker.
It utilizes Pandas and NumPy to process raw list dictionaries from the DataManager,
performing data aggregation, statistical anomaly detection, and financial reporting
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class ExpenseAnalyzer:
    '''
    Analyzes historical transaction data to track the user's spending
    habits and mark a threshold to define anomalies in future expense
    '''
    def __init__(self, exp_data: list):
        # creating a pandas DataFrame from the expense data returned from load_expenses()
        self.df=pd.DataFrame(exp_data)
        if not self.df.empty:
            # setting 'Amount' and 'Date' as float and Datetime, respectively, if DataFrame is not empty
            self.df['Amount'] = self.df['Amount'].astype(float)
            self.df['Date'] = pd.to_datetime(self.df['Date'])
    
    def get_category_totals(self):
        '''Calculates the total amount spent within each broader category'''

        # grouping by Category and calculating the sum of Amount
        total=self.df.groupby('Category')['Amount'].sum()
        return total.to_dict()
    
    def detect_anomalies(self):
        '''
        Identifies mathematically unusual expenses.
        Uses NumPy to define an anomaly as any expense greater than 
        (Mean + 1.5 * Standard Deviation)
            
        returns: 
            list: A list of dictionaries representing anomalous expense records
        '''
        if self.df.empty: return []

        # converting the 'Amount' column to a NumPy array, then calculating the threshold
        amt_arr=self.df['Amount'].to_numpy()
        mean=np.mean(amt_arr)
        std=np.std(amt_arr)
        threshold=mean+(1.5*std)
        return self.df[self.df['Amount']>threshold].to_dict('records')
    
    def get_total_spend(self):
        '''Calculates the grand total of all recorded expenses'''
        if self.df.empty: return 0.0
        return self.df['Amount'].sum()
    
    def get_exp_cost_breakdown(self):
        '''
        Calculates the total amount spent per individual 
        merchant/name, sorted highest to lowest
        '''
        if self.df.empty: return {}
        return self.df.groupby('Name')['Amount'].sum().sort_values(ascending=False).to_dict()
    
class SubscriptionAnalyzer:
    '''
    Analyzes recurring subscription data to track annual spenditure
    and any upcoming autopay bills
    '''
    def __init__(self, sub_data: list):
        # creating a pandas DataFrame from the subscription data returned from load_subscriptions()
        self.df=pd.DataFrame(sub_data)
        if not self.df.empty:
            # setting 'Cost', 'Annual Cost' and 'Next billing date' as 
            # float, float and datetime, respectively, if DataFrame is not empty
            self.df['Cost']=self.df['Cost'].astype(float)
            self.df['Annual Cost']=self.df['Annual Cost'].astype(float)
            self.df['Next billing date']=pd.to_datetime(self.df['Next billing date'])
    
    def get_total_annual_cost(self):
        '''Calculates the total combined yearly cost of all active subscriptions'''
        # returns 0.0 if the DataFrame is empty
        if self.df.empty: return 0.0
        return self.df['Annual Cost'].sum()
    
    def get_sub_cost_breakdown(self):
        '''Calculates the annual cost per subscription name, sorted highest to lowest'''
        if self.df.empty: return {}
        return self.df.groupby('Name')['Annual Cost'].sum().sort_values(ascending=False).to_dict()
    
    def get_upcoming_bills(self, days_ahead=3):
        '''
        Filters subscriptions to find those that are charging the user's account soon.
            Returns:
                list: A list of dictionaries representing subscriptions
                      due within the warning window.
        '''        
        today = datetime.now().date()
        limit = today + timedelta(days=days_ahead)
        
        upcoming = []
        
        for bill in self.df.to_dict('records'):
            raw_date = bill['Next billing date']
            
            try:
                due_date = raw_date.date()
            except AttributeError:
                due_date = datetime.strptime(raw_date, '%Y-%m-%d').date()
            
            if today <= due_date <= limit:
                bill['Next billing date'] = due_date.strftime('%Y-%m-%d')
                upcoming.append(bill)
                
        return sorted(upcoming, key=lambda x: x['Next billing date'])