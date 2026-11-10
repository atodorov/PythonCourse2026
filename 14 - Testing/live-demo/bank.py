class BankAccount(object):
    def __init__(self, name, balance):
        self.name = name
        self._balance = balance
        self._history = []

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError('Deposit amount must be positive!')

        self._balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError('Withdraw amount must be positive!')

        if amount <= self._balance:
            self._balance -= amount
            return True
        else:
            self._history.append("Withdraw for %d failed" % amount)

        return False

    def transfer_to(self, other_account, how_much):
        self.withdraw(how_much)
        other_account.deposit(how_much)
