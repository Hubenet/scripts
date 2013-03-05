#!/usr/bin/env python
# Use this script to fill a Adyen test account with some random transaction data using the SOAP API
# Test card numbers see https://support.adyen.com/index.php?/support/Knowledgebase/Article/View/11/0/test-card-numbers
#
# python-zsi is needed for the SOAP interface

from adyen import *			
import csv, datetime, time, random

def fill(wsUser,wsPassword,wsAccount,maxcount =5):
	gw = AdyenPaymentGateway( url='https://pal-test.adyen.com/pal/servlet/soap/Payment', user=wsUser, password=wsPassword, merchantAccount=wsAccount,)

	# Source of sample-data.csv file: http://www.fakenamegenerator.com/
	reader = csv.reader( open("sample-data.csv","rb"), delimiter=',', quotechar=None )

	# To limit 
	count = 0

	display_only = True		# Test: display only
	display_only = False		# Run: send to Adyen. Outcomment this line to TEST. Activate this line to SEND (to test system).

	# Return random element from list l
	def random_from(l):
		return l[random.randint(0,len(l)-1)]

	# Random amount with nice cents value
	def random_amount(min_amount,max_amount):
		cents = ['00','50','95','99']
		cent = random_from(cents)
		amounts = "%d%s" % (random.randint(min_amount,max_amount),cent)
		return int(amounts)

	# Random currency
	def random_currency():
		currencies = ['EUR','GBP','USD','SGD','BRL','CHF','SEK']
		currency = random_from(currencies)
		return currency

	# Fix expiry - if it's behind us then fix it
	def fix_expiry(expiry_month, expiry_year):
		(expiry_month, expiry_year) = (int(expiry_month), int(expiry_year))
		now = datetime.datetime.now()
		while expiry_year < now.year:
			expiry_year += 1
		if expiry_year == now.year and expiry_month < now.month:
			while expiry_month < now.month:
				expiry_month += 1
		return (expiry_month, expiry_year)

	# Random card
	# Either this is the card number passed as argument (which will be refused)
	# or it is one of the Adyen test card numbers (which will be 'authorised')
	# Returns a tuple (cardnumber,expiry_month,expiry_year,cvc)
	#
	def random_card(cardnumber,expiry="6/2016",cvc=None):
		testcards = [
			['5555 4444 3333 1111',	6,2016,737],	# MasterCard
			['5555 5555 5555 4444',	6,2016,737],	# MasterCard
			['4111 1111 1111 1111',	6,2016,737],	# Visa
			['4444 3333 2222 1111',	6,2016,737],	# Visa
			['3700 0000 0000 002', 	6,2016,7373],	# Amex
			['3600 6666 3333 44', 	6,2016,737],	# Diners
			['6011 6011 6011 6611',	6,2016,737],	# Discover
			['6731 0123 4567 8906', 6,2016,737],	# Maestro Intl
			
		]

		(expiry_month,expiry_year) = expiry.split("/")

		decline_to_auth_ratio = 3	# For every auth, 10 declines
		if random.randint(0,decline_to_auth_ratio-1) == 1:
			testcard = random_from(testcards)
			(cardnumber,expiry_month,expiry_year,cvc) = testcard
			cardnumber = cardnumber.replace(" ","")

		(expiry_month, expiry_year) = fix_expiry(expiry_month, expiry_year)
			
		return (cardnumber, expiry_month, expiry_year, cvc)

	# Fix email address, replace spaces by separator
	#
	def fix_email(email):
		separator = random_from( ['.','','-','_'] )
		email = email.strip()
		email = email.replace(' ',separator)
		if email[0] == '@':
			email = "%d%s" % (random.randint(0,99),email)
		return email

	# Generate a random ip address
	def random_ip():
	    not_valid = [10,127,169,172,192]
	 
	    first = random.randrange(1,256)
	    while first in not_valid:
		    first = random.randrange(1,256)
	 
	    ip = ".".join([str(first),str(random.randrange(1,256)),
	    str(random.randrange(1,256)),str(random.randrange(1,256))])
	    return ip

	# Generate a random fraud offset
	def random_fraud_offset():
		result = 0
		if random.randint(0,100) < 33:		# In 33% of the cases:
			result = random.randint(0,100)	# Return offset between 0 and 100
		return result


	for row in reader:
		try:
			(Number,Gender,GivenName,MiddleInitial,Surname,StreetAddress,City,State,ZipCode,Country,
			EmailAddress,Password,TelephoneNumber,MothersMaiden,Birthday,CCType,CCNumber,CVV2,CCExpires,
			NationalID,UPS,Occupation,Domain,BloodType,Pounds,Kilograms,FeetInches,Centimeters) = row
			if Number.isdigit():

				# Set the values
				merchantReference = "%.0f-%08d" % (time.time(), int(Number))
				currency = random_currency()
				amount = random_amount(5,50)
				name = "%s %s %s" % (GivenName,MiddleInitial,Surname)
				(cardnumber, expiry_month, expiry_year, cvc) = random_card(CCNumber,CCExpires,CVV2)
				customerIp = random_ip()
				shopperReference = Number
				shopperEmail = fix_email(EmailAddress)
				fraudOffset = random_fraud_offset()
				# Values set

				if display_only:
					print merchantReference, currency, amount, name, cardnumber, expiry_month, expiry_year, cvc, customerIp, shopperEmail, shopperReference, fraudOffset
				else:
					print gw.authorise( merchantReference, amount, currency, name, cardnumber, expiry_month, expiry_year, cvc, customerIp, 
						shopperEmail=shopperEmail, shopperReference=shopperReference, fraudOffset=fraudOffset )
				count+=1
				if count == maxcount:
					break
				
		except ValueError:
			pass



