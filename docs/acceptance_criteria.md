# Acceptance Criteria

## FR-1 - User Authentication
### AC 1
**Given:** User is logged in
**When:** User initiates payment
**Then:** Payment is processed

### AC 2
**Given:** User is not logged in
**When:** User initiates payment
**Then:** User is redirected to login page

### AC 3
**Given:** User session has expired
**When:** User initiates payment
**Then:** User is redirected to login page

---
## FR-2 - Payment Initiation
### AC 1
**Given:** User has a valid account
**When:** User enters valid payment details
**Then:** Payment is initiated successfully

### AC 2
**Given:** User has a valid account
**When:** User enters invalid payment details
**Then:** System displays an error message

### AC 3
**Given:** User has a valid account
**When:** User enters a payment amount exceeding the limit
**Then:** System displays a warning message

---
## FR-3 - Payment Processing
### AC 1
**Given:** Valid payment details
**When:** Payment is processed
**Then:** Transaction ID is generated

### AC 2
**Given:** Invalid payment details
**When:** Payment is processed
**Then:** Error message is displayed

### AC 3
**Given:** Payment gateway is down
**When:** Payment is processed
**Then:** Error message is displayed

---
## FR-4 - Payment Confirmation
### AC 1
**Given:** User has made a payment
**When:** Payment is processed
**Then:** System displays payment success confirmation

### AC 2
**Given:** User has made a payment
**When:** Payment is declined
**Then:** System displays payment failure message

### AC 3
**Given:** User has made a payment with insufficient balance
**When:** Payment is processed
**Then:** System displays low balance error message

---
## FR-5 - Transaction History
### AC 1
**Given:** User is logged in
**When:** User navigates to transaction history page
**Then:** User can view all transactions

### AC 2
**Given:** User is on transaction history page
**When:** User enters invalid date range
**Then:** System displays error message

### AC 3
**Given:** User has no transactions
**When:** User navigates to transaction history page
**Then:** System displays no transactions message

---
## NFR-1 - Response Time
### AC 1
**Given:** Normal system load
**When:** User submits a request
**Then:** Response is received within 3 seconds

### AC 2
**Given:** Invalid user input
**When:** User submits a request
**Then:** Error message is displayed within 3 seconds

### AC 3
**Given:** High system load
**When:** Multiple users submit requests
**Then:** Average response time is less than 3 seconds

---
## NFR-2 - System Availability
### AC 1
**Given:** System is properly configured
**When:** System is in production
**Then:** System availability is 99.9%

### AC 2
**Given:** Invalid user input
**When:** User attempts to access the system
**Then:** System displays error message and remains available

### AC 3
**Given:** High traffic volume
**When:** Multiple users access the system simultaneously
**Then:** System responds within 2 seconds and remains available

---
## NFR-3 - Payment Information Encryption
### AC 1
**Given:** Valid payment information is entered
**When:** Payment is processed
**Then:** Payment information is encrypted

### AC 2
**Given:** Invalid payment information is entered
**When:** Payment is processed
**Then:** Error message is displayed and payment information is not stored

### AC 3
**Given:** Payment information is empty
**When:** Payment is processed
**Then:** Error message is displayed and payment is not processed

---
## AC-1 - Successful Payment
### AC 1
**Given:** User has sufficient funds
**When:** User submits payment
**Then:** Payment is processed successfully

### AC 2
**Given:** User has invalid payment details
**When:** User submits payment
**Then:** Payment is rejected with error message

### AC 3
**Given:** User has exact amount for payment
**When:** User submits payment
**Then:** Payment is processed without remaining balance

---
## AC-2 - Invalid Payment Details
### AC 1
**Given:** Valid user account
**When:** User attempts to make a payment with valid details
**Then:** Payment is processed successfully

### AC 2
**Given:** Valid user account
**When:** User attempts to make a payment with invalid card number
**Then:** Payment is rejected with an error message

### AC 3
**Given:** Valid user account
**When:** User attempts to make a payment with expired card
**Then:** Payment is rejected with an error message

---
## AC-3 - Transaction ID Generation
### AC 1
**Given:** A user makes a successful payment
**When:** The payment is processed
**Then:** A unique transaction ID is generated

### AC 2
**Given:** A user enters invalid payment details
**When:** The payment is attempted
**Then:** No transaction ID is generated

### AC 3
**Given:** A user makes multiple successful payments in a row
**When:** Each payment is processed
**Then:** A new unique transaction ID is generated for each payment

---
## AC-4 - Confirmation Email
### AC 1
**Given:** User completes payment
**When:** Payment is successful
**Then:** Confirmation email is sent

### AC 2
**Given:** User enters invalid email
**When:** Payment is successful
**Then:** Error message is displayed

### AC 3
**Given:** User has multiple pending payments
**When:** One payment is successful
**Then:** Confirmation email is sent only for the successful payment

---
