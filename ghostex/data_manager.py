'''
data_manager.py

this module defines data management aspect of the program using csv file handling 
to manage the storage and access of subscription and expense data throughout the
program's execution
'''

import os
import csv
from models import Expense, Subscription
from datetime import datetime, timedelta

class DataManager:
    '''
    class DataManager:  uses csv file handling to 
                    process and save expense and subscription data

    __init__                -   initializes the expenses.csv and subscriptions.csv file
                                creates the file if not already present, else writes csv
                                header.

    save_expenses()         -   saves expense data into expenses.csv, fetching the expense
                                details from Expense class of models.py

    save_subscriptions()    -   saves subscription data into subscriptions.csv, fetching the
                                subscription details from Subscription class of models.py

    load_expenses()         -   returns a list of dictionary of expense data stored in the file

    load_subscriptions()    -   returns a list of dictionary of subscription data stored in the file
    '''
    def __init__(self, expenses_file="expenses.csv", subs_file="subscriptions.csv"):
        self.exp_file=expenses_file
        self.subs_file=subs_file
        # creating expense and subscription header for the csv files
        self.exp_header=["ID","Name","Amount","Category","Date","Tags"]
        self.sub_header=["ID","Name","Cost","Billing Cycle","Next billing date","Annual Cost"]
        
        if not os.path.exists(self.exp_file):
            # proceeding only if the file does not exists
            with open(self.exp_file,"w", newline='') as f:
                writer=csv.DictWriter(f,self.exp_header)
                writer.writeheader()

        
        if not os.path.exists(self.subs_file):
            # proceeding only if the file does not exists
            with open(self.subs_file,"w", newline='') as f:
                writer=csv.DictWriter(f,self.sub_header)
                writer.writeheader()

    def is_expense_id_duplicate(self, check_id):
        for exp in self.load_expenses():
            if str(exp.get('ID', '')) == str(check_id):
                return True
        return False

    def is_subscription_id_duplicate(self, check_id):
        for sub in self.load_subscriptions():
            if str(sub.get('ID', '')) == str(check_id):
                return True
        return False
        
    def save_expenses(self, exp_obj: Expense):
        try:
            with open(self.exp_file,"a",newline='') as f:
                writer=csv.DictWriter(f,self.exp_header)
                writer.writerow(exp_obj.to_dict())
        except IOError:
            raise IOError("Cannot save data: Close your csv file")
        
    def save_subscriptions(self, sub_obj: Subscription):
        try:
            with open(self.subs_file,'a',newline='') as f:
                writer=csv.DictWriter(f,self.sub_header)
                writer.writerow(sub_obj.to_dict())
        except IOError:
            raise IOError("Cannot save data: Close your csv file")

    def load_expenses(self):
        exp_data=[]
        try:
            with open(self.exp_file,'r') as f:
                reader=csv.DictReader(f)
                for row in reader:
                    exp_data.append(row)
            return exp_data
        
        # returning an empty list if file not found or corrupted.
        except FileNotFoundError:
            print(f"Warning: {self.exp_file} not found.")
            return []
        
        except Exception as e:
            print(f"Error: Could not read {self.exp_file}. Data may be corrupted. Details: {e}")
            return []
        
    
    def load_subscriptions(self):
        sub_data=[]
        try:
            with open(self.subs_file,'r') as f:
                reader=csv.DictReader(f)
                for row in reader:
                    sub_data.append(row)
            return sub_data
        
        # returning an empty list if file not found or corrupted.
        except FileNotFoundError:
            print(f"Warning: {self.subs_file} not found.")
            return []
        
        except Exception as e:
            print(f"Error: Could not read {self.subs_file}. Data may be corrupted. Details: {e}")
            return []
        
    def update_past_due_subscriptions(self):
        """Checks if any subscriptions are past due and rolls them forward."""
        subs = self.load_subscriptions()
        updated = False
        today = datetime.now().date()

        for sub in subs:
            try:
                due_date = datetime.strptime(sub['Next billing date'], "%Y-%m-%d").date()
                while due_date < today:
                    updated = True
                    cycle = sub.get('Billing Cycle', 'Monthly')
                    
                    if cycle == "Weekly":
                        due_date += timedelta(days=7)
                    elif cycle == "Yearly":
                        due_date += timedelta(days=365)
                    else:
                        due_date += timedelta(days=30)
                
                sub['Next billing date'] = due_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
                
        
        if updated and subs:
            import csv
            
            with open(self.subs_file, mode='w', newline='') as file:
                dynamic_headers = list(subs[0].keys())
                writer = csv.DictWriter(file, fieldnames=dynamic_headers)
                writer.writeheader()
                writer.writerows(subs)
            print("System Alert: Auto-rolled past due subscriptions forward.")

    def delete_expense(self, expense_id):
        expenses=self.load_expenses()
        clean_exp=[]
        for exp in expenses:
            if str(exp.get('ID',''))!=str(expense_id):
                clean_exp.append(exp)

        if len(expenses) == len(clean_exp):
            print(f"Error: Could not find expense with ID {expense_id} to delete.")
            return
        
        if clean_exp:
            with open(self.exp_file, "w", newline='') as file:
                header=list(clean_exp[0].keys())
                
                writer=csv.DictWriter(file,fieldnames=header)
                writer.writeheader()
                writer.writerows(clean_exp)
        
        else:
            with open(self.exp_file,"w", newline='') as file:
                writer=csv.writer(file)
                writer.writerow(["ID", "Name", "Amount", "Category", "Date", "Tags"])

        print(f"System Alert: Successfully deleted expense {expense_id}.")

    def delete_subscription(self, sub_id):
        subs = self.load_subscriptions()
        clean_subs = []
        
        for sub in subs:
            if str(sub.get('ID', '')) != str(sub_id):
                clean_subs.append(sub)

        if len(subs) == len(clean_subs):
            print(f"Error: Could not find subscription with ID {sub_id} to delete.")
            return
        
        import csv
        if clean_subs:
            with open(self.subs_file, "w", newline='') as file:
                header = list(clean_subs[0].keys())
                writer = csv.DictWriter(file, fieldnames=header)
                writer.writeheader()
                writer.writerows(clean_subs)
        else:
            with open(self.subs_file, "w", newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Name", "Cost", "Billing Cycle", "Next billing date", 'Annual Cost'])
                
        print(f"System Alert: Successfully deleted subscription {sub_id}.")