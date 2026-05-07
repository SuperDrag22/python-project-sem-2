import customtkinter as ctk
from data_manager import DataManager
from analytics import ExpenseAnalyzer, SubscriptionAnalyzer
from models import Expense, Subscription
from tkinter import messagebox

ctk.set_appearance_mode("dark")

class SmartTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("GHOSTEX")
        self.geometry("1000x700")

        self.tab=ctk.CTkTabview(
                    self,
                    border_width=4,
                    border_color="#362020",
                    fg_color="#373248",
                    segmented_button_fg_color="#573434",
                    segmented_button_selected_color="#402424",
                    segmented_button_unselected_color="#9e7878",
                    segmented_button_unselected_hover_color="#9f8166",
        ); self.tab.pack(fill="both", expand=True, padx=20, pady=20)
        self.tab.add("Dashboard")
        self.tab.add("Expenses")
        self.tab.add("Subscriptions")
        self.tab.set("Dashboard")

        self.db = DataManager()
        self.load_backend_data()
        self.build_dashboard()
        self.build_expenses_tab()
        self.build_subscriptions_tab()

    def save_expense_action(self):
        raw_id = self.exp_id_entry.get()

        if self.db.is_expense_id_duplicate(raw_id):
            messagebox.showerror("Duplicate ID", f"An expense with ID '{raw_id}' already exists. Please use a unique ID.")
            return

        raw_name = self.exp_name_entry.get()
        raw_amount = self.exp_amount_entry.get()
        raw_category = self.exp_cat_menu.get()
        raw_date = self.exp_date_entry.get()
        raw_tags = self.exp_tags_entry.get()
        
        try:
            formatted_amount = float(raw_amount)
            formatted_tags = [tag.strip() for tag in raw_tags.split(",") if tag.strip()]

            new_expense = Expense(
                id=raw_id,
                name=raw_name, 
                amount=formatted_amount, 
                category=raw_category, 
                date=raw_date, 
                tags=formatted_tags
            );  self.db.save_expenses(new_expense)

            self.exp_id_entry.delete(0, 'end')
            self.exp_name_entry.delete(0, 'end')
            self.exp_amount_entry.delete(0, 'end')
            self.exp_date_entry.delete(0, 'end')
            self.exp_tags_entry.delete(0, 'end')
            
            messagebox.showinfo("Success", f"Saved '{raw_name}' to the database!")
            
        except ValueError:
            messagebox.showerror("Input Error", "Please make sure the Amount is a valid number.")
        self.load_backend_data()
        self.refresh_dashboard() 
        self.refresh_expense_list()


    def save_subscription_action(self):
        raw_sub_id=self.sub_id_entry.get()
        from tkinter import messagebox
        if self.db.is_subscription_id_duplicate(raw_sub_id):
            messagebox.showerror("Duplicate ID", f"A subscription with ID '{raw_sub_id}' already exists. Please use a unique ID.")
            return

        raw_sub_name=self.sub_name_entry.get()
        raw_sub_cost=self.sub_cost_entry.get()
        raw_sub_bcd=self.sub_cycle_menu.get()
        raw_sub_nextdate=self.sub_date_entry.get()

        try:
            formatted_cost=float(raw_sub_cost)

            new_sub=Subscription(
                id=raw_sub_id,
                name=raw_sub_name,
                cost=raw_sub_cost,
                billing_cycle=raw_sub_bcd,
                next_billing_date=raw_sub_nextdate
            ); self.db.save_subscriptions(new_sub)

            self.sub_id_entry.delete(0, 'end')
            self.sub_name_entry.delete(0, 'end')
            self.sub_cost_entry.delete(0, 'end')
            self.sub_date_entry.delete(0, 'end')

            messagebox.showinfo("Success",f"Saved '{raw_sub_name}' to the database!")

        except ValueError:
            messagebox.showerror("Input Error", "Please make sure the cost is a valid number")
            
        self.load_backend_data()
        self.refresh_dashboard() 
        self.refresh_subscriptions_list()

    def load_backend_data(self):
        self.db.update_past_due_subscriptions()
        raw_expenses = self.db.load_expenses()
        raw_subs = self.db.load_subscriptions()
        self.exp_analyzer=ExpenseAnalyzer(raw_expenses)
        self.sub_analyzer=SubscriptionAnalyzer(raw_subs)

    def build_dashboard(self):
        dash_tab=self.tab.tab("Dashboard")
        total_spend=self.exp_analyzer.get_total_spend()

        total_frame=ctk.CTkFrame(
                    dash_tab,
                    border_color="#362020",
                    border_width=4,
                    fg_color="#533A7E"
        ); total_frame.pack(pady=10,padx=20,fill="both",expand=True)        

        self.ttl_label=ctk.CTkLabel(
                    total_frame, 
                    text=f"Total Expenses: ₹{total_spend:.2f}", 
                    font=("Arial", 32, "bold")
        ); self.ttl_label.pack(pady=(80,10))

        total_subs = self.sub_analyzer.get_total_annual_cost()
        self.sub_label=ctk.CTkLabel(
                    total_frame, 
                    text=f"Total Subscriptions: ₹{total_subs:.2f}", 
                    font=("Arial", 32, "bold")
        ); self.sub_label.pack()

        bill_frame=ctk.CTkScrollableFrame(
                    dash_tab,
                    label_text="Upcoming Bills (Next 3 Days)",
                    label_font=("Arial", 25, "bold"),
                    label_fg_color="#362020",
                    border_width=4,
                    border_color="#362020",
                    fg_color="#533a7e"
        ); bill_frame.pack(pady=10,padx=20, fill="x")

        upcoming = self.sub_analyzer.get_upcoming_bills()
        if not upcoming:
            self.warn_label=ctk.CTkLabel(
                        bill_frame,
                        text="No bills due soon!",
                        font=("Arial", 20)
            ); self.warn_label.pack()
        else:
            for row in upcoming:
                self.warn_label=ctk.CTkLabel(
                            bill_frame,
                            text=f"{row['Name']} - ₹{row['Cost']} (Due: {row['Next billing date']})",
                            font=("Arial", 20),
                ); self.warn_label.pack()

        self.report_btn = ctk.CTkButton(
            dash_tab, 
            text="Generate Smart Report", 
            fg_color="#10b981",
            hover_color="#059669",
            text_color="#000000",
            font=("Arial",15,"bold"),
            command=self.show_financial_report
        )
        self.report_btn.pack(pady=20)

    def refresh_dashboard(self):
        new_total = self.exp_analyzer.get_total_spend()
        self.ttl_label.configure(text=f"Total Spend: ₹{new_total:.2f}")

        new_sub_total = self.sub_analyzer.get_total_annual_cost()
        self.sub_label.configure(text=f"Total Subscriptions: ₹{new_sub_total:.2f}") 

    def build_expenses_tab(self):
        exp_tab=self.tab.tab("Expenses")
        self.exp_form_frame=ctk.CTkFrame(
                    exp_tab,
                    border_color="#362020",
                    border_width=4,
                    fg_color="#533a7e"
        ); self.exp_form_frame.pack(pady=10,padx=20,expand=True)

        # id entry
        self.exp_id_entry = ctk.CTkEntry(
                    self.exp_form_frame, 
                    placeholder_text="Product ID (e.g. 001)", 
                    height=40, 
                    width=300,
                    fg_color="#b9a599",
                    placeholder_text_color="black",
                    text_color="black"
        ); self.exp_id_entry.pack(pady=(20,5), padx=20)

        # name entry
        self.exp_name_entry=ctk.CTkEntry(
                    self.exp_form_frame, 
                    placeholder_text="Expense Name (e.g., Coffee)",
                    height=40,
                    width=300,
                    fg_color="#b9a599",
                    placeholder_text_color="black",
                    text_color="black"
        ); self.exp_name_entry.pack(pady=5)

        # amount entry
        self.exp_amount_entry=ctk.CTkEntry(
                    self.exp_form_frame, 
                    placeholder_text="Amount",
                    height=40,
                    width=300,
                    fg_color="#b9a599",
                    placeholder_text_color="black",
                    text_color="black"
        ); self.exp_amount_entry.pack(pady=5)

        # category option menu
        self.exp_cat_menu = ctk.CTkOptionMenu(
                    self.exp_form_frame, 
                    values=[
                        "Housing",
                        "Groceries",
                        "Dining Out",
                        "Transport",
                        "Utilities",
                        "Gadgets",
                        "Healthcare",
                        "Entertainment",
                        "Shopping",
                        "Education",
                        "Debt Repayment",
                        "Savings",
                        "Travel",
                        "Personal Care",
                        "Gifts",
                        "Other"
                    ],
                    height=40,
                    width=300,
                    fg_color="#b9a599",
                    text_color="black",
                    dropdown_text_color="black",
                    dropdown_fg_color="#b9a599",
                    button_color="#b9a599",
                    button_hover_color="#756860",
                    dropdown_hover_color="#756860"
        ); self.exp_cat_menu.pack(pady=5)

        # date entry
        self.exp_date_entry=ctk.CTkEntry(
                    self.exp_form_frame, 
                    placeholder_text="Date (YYYY-MM-DD)",
                    height=40,
                    width=300,
                    fg_color="#b9a599",
                    placeholder_text_color="black",
                    text_color="black"
        ); self.exp_date_entry.pack(pady=5)

        # tags entry
        self.exp_tags_entry=ctk.CTkEntry(
                    self.exp_form_frame, 
                    placeholder_text="Tags (comma separated)",
                    height=40,
                    width=300,
                    fg_color="#b9a599",
                    placeholder_text_color="black",
                    text_color="black"
        ); self.exp_tags_entry.pack(pady=5)

        # submit button
        self.exp_submit_btn=ctk.CTkButton(
                    self.exp_form_frame,
                    text="Save Expenses", 
                    command=self.save_expense_action)
        self.exp_submit_btn.pack(pady=(5,15))

        self.exp_history_frame=ctk.CTkScrollableFrame(
                    exp_tab, 
                    label_text="Recent Expenses",
                    label_font=("Arial", 30, "bold"),
                    label_fg_color="#362020",
                    border_width=4,
                    border_color="#362020",
                    fg_color="#533a7e"
        ); self.exp_history_frame.pack(pady=20, 
                                       padx=20, 
                                       fill="both", 
                                       expand=True,)

        self.refresh_expense_list()

    def refresh_expense_list(self):
        for widget in self.exp_history_frame.winfo_children():
            widget.destroy()
        expenses=self.db.load_expenses()

        for expense in expenses:
            
            row_frame=ctk.CTkFrame(
                        self.exp_history_frame,
                        fg_color="transparent"
            ); row_frame.pack(fill="x", pady=2)

            ctk.CTkLabel(
                        row_frame,
                        text=f"{expense['ID']}: {expense['Name']} - ₹{expense['Amount']} ({expense['Category']})",
                        font=("Arial",16,"bold")
            ).pack(side="left",padx=10)

            exp_id = expense.get('ID', '')
            ctk.CTkButton(
                row_frame,
                text="X",
                width=30,
                fg_color="#ef4444",
                hover_color="#b91c1c",
                command=lambda e_id=exp_id: self.delete_expense_action(e_id)
            ).pack(side="right", padx=10)
    
    def delete_expense_action(self, expense_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense?"):
            self.db.delete_expense(expense_id)
            self.refresh_expense_list()
            messagebox.showinfo("Deleted Successfully!",f"Deleted Expense {expense_id} Successfully")
        
        self.load_backend_data()
        self.refresh_dashboard() 

    def build_subscriptions_tab(self):
        sub_tab = self.tab.tab("Subscriptions")
        self.sub_form_frame=ctk.CTkFrame(
                    sub_tab,
                    border_color="#362020",
                    border_width=4,
                    fg_color="#533a7e"
        ); self.sub_form_frame.pack(pady=10,padx=20,expand=True)

        # id entry
        self.sub_id_entry = ctk.CTkEntry(
                    self.sub_form_frame, 
                    placeholder_text="Subscription ID", 
                    height=40, 
                    width=300,
                    fg_color="#b9a599",
                    placeholder_text_color="black",
                    text_color="black"
        ); self.sub_id_entry.pack(pady=(20,5),padx=20)

        # name Entry
        self.sub_name_entry = ctk.CTkEntry(
                    self.sub_form_frame, 
                    placeholder_text="Subscription Name (e.g., Netflix)", 
                    height=40, 
                    width=300,
                    fg_color="#b9a599",
                    placeholder_text_color="black",
                    text_color="black"
        ); self.sub_name_entry.pack(pady=5)

        # cost Entry
        self.sub_cost_entry = ctk.CTkEntry(
                    self.sub_form_frame, 
                    placeholder_text="Cost per cycle", 
                    height=40, 
                    width=300,
                    fg_color="#b9a599",
                    placeholder_text_color="black",
                    text_color="black"
        ); self.sub_cost_entry.pack(pady=5)

        # Billing Cycle Dropdown
        self.sub_cycle_menu = ctk.CTkOptionMenu(
                    self.sub_form_frame, 
                    values=["Monthly", "Yearly", "Weekly"],
                    height=40, 
                    width=300,
                    fg_color="#b9a599",
                    text_color="black",
                    dropdown_text_color="black",
                    dropdown_fg_color="#b9a599",
                    button_color="#b9a599",
                    button_hover_color="#756860",
                    dropdown_hover_color="#756860"
        ); self.sub_cycle_menu.pack(pady=5)

        # next Billing Date Entry
        self.sub_date_entry = ctk.CTkEntry(
                    self.sub_form_frame, 
                    placeholder_text="Next Billing Date (YYYY-MM-DD)", 
                    height=40, 
                    width=300,
                    fg_color="#b9a599",
                    placeholder_text_color="black",
                    text_color="black"
        ); self.sub_date_entry.pack(pady=5)

        # submit Button
        self.sub_submit_btn = ctk.CTkButton(
                    self.sub_form_frame, 
                    text="Save Subscription", 
                    command=self.save_subscription_action
        ); self.sub_submit_btn.pack(pady=(5,15))

        self.sub_history_frame=ctk.CTkScrollableFrame(
                    sub_tab,
                    label_text="Active Subscriptions",
                    label_font=("Arial", 30, "bold"),
                    label_fg_color="#362020",
                    border_width=4,
                    border_color="#362020",
                    fg_color="#533a7e"
        ); self.sub_history_frame.pack(pady=20, 
                                       padx=20, 
                                       fill="both", 
                                       expand=True)
        self.refresh_subscriptions_list()
        
    def refresh_subscriptions_list(self):
        for widget in self.sub_history_frame.winfo_children():
            widget.destroy()

        subs=self.db.load_subscriptions()

        for sub in subs:
            row_frame = ctk.CTkFrame(self.sub_history_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)

            ctk.CTkLabel(
                        row_frame,
                        text=f"{sub['Name']} - ₹{sub['Cost']} ({sub['Billing Cycle']}) | Next Due: {sub['Next billing date']}",
                        font=("Arial",16,"bold")
            ).pack(side="left",padx=10)

            sub_id = sub.get('ID', '')
            ctk.CTkButton(
                row_frame,
                text="X",
                width=30,
                fg_color="#ef4444",
                hover_color="#b91c1c",
                command=lambda s_id=sub_id: self.delete_subscription_action(s_id)
            ).pack(side="right", padx=10)
    
    def delete_subscription_action(self, sub_id):
        if messagebox.askyesno("Confirm Delete",f"Are you sure you want to delete subscription '{sub_id}?"):
            self.db.delete_subscription(sub_id)
            self.refresh_subscriptions_list()
            messagebox.showinfo("Deleted Successfully",f"Deleted Subscription {sub_id} Successfully")
        
        self.load_backend_data()
        self.refresh_dashboard() 

    def show_financial_report(self):
        report_win=ctk.CTkToplevel(self)
        report_win.title("GHOSTEX Financial Report")
        report_win.geometry("700x760")
        report_win.attributes('-topmost',True)

        report_main_frame=ctk.CTkFrame(
                    report_win,
                    border_width=4,
                    border_color="#362020",
                    fg_color="#373248"
        ); report_main_frame.pack(pady=10,padx=20,fill="both",expand=True)

        ctk.CTkLabel(
                    report_main_frame,
                    text="Financial Insights Report!",
                    font=('Arial',35,"bold")
        ).pack(pady=20)

        anomalies=self.exp_analyzer.detect_anomalies()
        if anomalies:
            warn_frame = ctk.CTkFrame(
                        report_main_frame, 
                        fg_color="#422006", 
                        border_color="#fbbf24", 
                        border_width=2
            ); warn_frame.pack(pady=20, padx=20, fill="x")

            ctk.CTkLabel(
                        warn_frame, 
                        text="SPENDING ANOMALIES DETECTED", 
                        text_color="#fbbf24", 
                        font=("Arial", 25, "bold")).pack(pady=5)
            
            for anomaly in anomalies:
                ctk.CTkLabel(
                            warn_frame, 
                            text=f"High Spend: {anomaly['Name']} (₹{anomaly['Amount']})",
                            font=("Arial", 20)
                ).pack(pady=5)
        
        category_data = self.exp_analyzer.get_category_totals()

        cat_frame=ctk.CTkScrollableFrame(
                    report_main_frame,
                    label_text="Spending by Category",
                    label_font=("Arial", 30, "bold"),
                    label_fg_color="#362020",
                    border_width=4,
                    border_color="#362020",
                    fg_color="#533a7e",
        ); cat_frame.pack(pady=10,padx=20,fill="x")

        for cat, total in category_data.items():
            row = ctk.CTkFrame(
                        cat_frame, 
                        fg_color="transparent",
            ); row.pack(pady=(5,0),fill="x", padx=40)

            ctk.CTkLabel(
                        row, 
                        text=cat).pack(side="left")
            ctk.CTkLabel(
                        row, 
                        text=f"₹{total:.2f}", 
                        font=("Arial", 14, "bold")).pack(side="right")
        
        top_merchants = self.exp_analyzer.get_exp_cost_breakdown()
        
        top_merchants_frame=ctk.CTkFrame(
                    report_main_frame,
                    border_color="#362020",
                    border_width=4,
                    fg_color="#533a7e"
        ); top_merchants_frame.pack(pady=10,padx=20,fill="both",expand=True)

        ctk.CTkLabel(
                    top_merchants_frame, 
                    text="Top Merchants", 
                    font=("Arial", 20, "bold")).pack(pady=(10, 5))

        for i, (name, amount) in enumerate(top_merchants.items()):
            if i > 2: break
            ctk.CTkLabel(
                        top_merchants_frame, 
                        text=f"{i+1}. {name}: ₹{amount:.2f}").pack()

        ctk.CTkButton(
                    report_main_frame, 
                    text="Close Report", 
                    command=report_win.destroy).pack(pady=30)

if __name__ == "__main__":
    app=SmartTrackerApp()
    app.mainloop()