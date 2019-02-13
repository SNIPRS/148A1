"""
CSC148, Winter 2019
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2019 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
import datetime
from math import ceil
from typing import Optional
from bill import Bill
from call import Call


# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


class Contract:
    """ A contract for a phone line

    This is an abstract class. Only subclasses should be instantiated.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.datetime
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        self.start = start
        self.bill = None


    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return self.bill.get_cost()


# TODO: Implement the MTMContract, TermContract, and PrepaidContract
class TermContract(Contract):
    """
    Random stuff here
    """
    start: datetime.datetime
    bill: Optional[Bill]
    def __init__(self, start: datetime.date, end: datetime.date) -> None:
        """ Create a new Contract with the <start> and <end> date, starts as
        inactive
        """
        Contract.__init__(self, start)
        self.end = end
        self._current = [start.month, start.year]

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        per minute and fixed cost.
        Store the <bill> argument in this contract and set the appropriate rate
        """
        if self.start.month == month and self.start.year == year:
            bill.add_fixed_cost(TERM_DEPOSIT)
        self._current = [month, year]
        bill.add_fixed_cost(TERM_MONTHLY_FEE)
        bill.set_rates("TERM", TERM_MINS_COST)
        bill.add_free_minutes(TERM_MINS)
        self.bill = bill


    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        duration = ceil(call.duration / 60.0)
        delta = self.bill.free_min - duration
        if delta >= 0:
            self.bill.free_min = delta
        else:
            self.bill.free_min = 0
            self.bill.add_billed_minutes(-1*delta)

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        if self.end.month <= self._current[0] and \
                self.end.year <= self._current[1]:
            self.bill.add_fixed_cost(-1 * TERM_DEPOSIT)
        return self.bill.get_cost()


class MTMContract(Contract):
    """
    Random stuff here
    """
    def __init__(self, start: datetime.date) -> None:
        """
        Same as Contract __init__ .... for now
        """
        Contract.__init__(self, start)

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        per minute and fixed cost.
        Store the <bill> argument in this contract and set the appropriate rate
        """
        bill.add_fixed_cost(MTM_MONTHLY_FEE)
        bill.set_rates("MTM", MTM_MINS_COST)
        self.bill = bill

    #Same cancel method as Contract

class PrepaidContract(Contract):
    """
    Random stuff! Again!
    """
    def __init__(self, start: datetime.date, balance: int) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        Contract.__init__(self, start)
        self._balance = balance
        self._credit = balance

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        if self._credit <= 10:
            self._balance += 25
            self._credit += 25
        bill.set_rates("PREPAID", PREPAID_MINS_COST)
        bill.add_fixed_cost(self._balance)
        self._balance = 0
        self.bill = bill

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        duration = ceil(call.duration / 60.0)
        cost = duration * self.bill.min_rate
        delta = self._credit - cost
        if delta >= 0:
            self._credit = delta
        else:
            self._credit = 0
            self.bill.add_billed_minutes(-1*duration)


    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        self.bill.add_fixed_cost(self._balance)
        return self.bill.get_cost()


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call', 'math'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
