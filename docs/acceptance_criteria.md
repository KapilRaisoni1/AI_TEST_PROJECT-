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
**When:** User initiates payment with valid details
**Then:** Payment is processed successfully

### AC 2
**Given:** User has a valid account
**When:** User initiates payment with missing mandatory fields
**Then:** System displays an error message

### AC 3
**Given:** User has a valid account
**When:** User initiates payment with a negative amount
**Then:** System displays an error message

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
**Given:** User completes payment
**When:** Payment is processed
**Then:** System displays payment success confirmation

### AC 2
**Given:** User enters invalid payment details
**When:** Payment is processed
**Then:** System displays payment failure message

### AC 3
**Given:** User has multiple pending payments
**When:** One payment is processed
**Then:** System sends confirmation email for the processed payment

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
**Given:** A user sends a request
**When:** The system processes the request
**Then:** The response is received within 3 seconds

### AC 2
**Given:** A user sends an invalid request
**When:** The system validates the request
**Then:** An error message is returned within 3 seconds

### AC 3
**Given:** A large number of users send requests simultaneously
**When:** The system handles the high load
**Then:** The average response time remains below 3 seconds

---
## NFR-2 - System Availability
### AC 1
**Given:** System is properly configured
**When:** System is in production
**Then:** System is available 99.9% of the time

### AC 2
**Given:** Invalid user input
**When:** User attempts to access the system
**Then:** System displays an error message and remains available

### AC 3
**Given:** High traffic volume
**When:** Many users access the system simultaneously
**Then:** System responds within an acceptable timeframe and remains available

---
## NFR-3 - Payment Information Encryption
### AC 1
**Given:** Valid payment information is entered
**When:** Payment is processed
**Then:** Payment information is encrypted

### AC 2
**Given:** Invalid payment information is entered
**When:** Payment is processed
**Then:** Error message is displayed and payment information is not encrypted

### AC 3
**Given:** Payment information is empty
**When:** Payment is processed
**Then:** Error message is displayed and payment information is not encrypted

---
## AC-1 - Successful Payment
### AC 1
**Given:** User has sufficient funds
**When:** User submits payment
**Then:** Payment is processed successfully

### AC 2
**Given:** User enters invalid card details
**When:** User submits payment
**Then:** Error message is displayed

### AC 3
**Given:** User has exactly enough funds
**When:** User submits payment
**Then:** Payment is processed successfully with no balance

---
## AC-2 - Invalid Payment Details
### AC 1
**Given:** User enters valid payment details
**When:** User submits payment
**Then:** Payment is processed successfully

### AC 2
**Given:** User enters invalid payment details
**When:** User submits payment
**Then:** Payment is rejected with an error message

### AC 3
**Given:** User enters payment details with a low balance
**When:** User submits payment
**Then:** Payment is rejected with an insufficient funds error message

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
