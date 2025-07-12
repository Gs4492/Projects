class Invoice:
    def __init__(self, invoice_number, customer_name, amount, status, issue_date):
        self.invoice_number = invoice_number
        self.customer_name = customer_name
        self.amount = amount
        self.status = status
        self.issue_date = issue_date
