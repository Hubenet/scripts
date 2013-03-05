#!/usr/bin/env python
# Use this script to fill a Adyen test account with some random transaction data using the SOAP API

import fill

wsUser = 'ws______@Company._______'		# Create a new "system" or "ws" user in Adyen backoffice
wsPassword = '_________'			# Password: min 8 chars, should contain number(s)
wsAccount = '________'				# Merchant Account
numTransactions = 50				# Number of transactions to fill

fill.fill(wsUser,wsPassword,wsAccount,numTransactions)

