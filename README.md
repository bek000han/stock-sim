# **Finance Simulaton Website**
#### **Video Demo**: todo
### **Description**:

This project is a web-based simulation of managing a stock portfolio; it lets the user practice and experience the world of finance without paying a cent. It allows users to create their own personal accounts and portfolios, buy and sell stocks for profit, view transaction history, and obtain real-time stock quotes using the IEX Cloud API. The web application is built using the Flask framework and utilizes an SQLite database to store user information and transaction data. The project was made as part of the CS50x course. 

### **Installation**:
To run the finance web application locally, follow these steps:
- Clone the repository to your local machine:
> $ git clone <repository-url>

- Navigate to the project directory:
> $ cd finance-web-app

- Install the required dependencies:
> $ pip install -r requirements.txt

- Set the API key for the IEX Cloud API:
  - Sign up for an account at IEX Cloud at https://iexcloud.io/
  - Copy your API key from the account dashboard.
  - Paste the copied value into the terminal as follows:
  > $ export API_KEY=value

- Run the Flask application:
> $ flask run

> Ctrl + left click the flask-provided hyperlink


### **Usage Instructions**:
Once the finance web application is running, you can perform the following actions:

- Register: Create a new user account by providing a unique username and password. All accounts start with $10,000 by default.

- Login: Login to an existing user account using your username and password.

- Quote: Retrieve real-time stock quotes by entering the symbol of a stock. The application will display the current price and other information about the stock.

- Buy: Purchase stocks by specifying the symbol and number of shares you want to buy. The application will check your available funds and deduct the appropriate amount from your account balance.

- Sell: Sell stocks that you own by selecting the symbol and number of shares you want to sell. The application will add the sale proceeds to your account balance. The stock prices are in real-time, so you should aim to sell at a profit.

- History: View a history of your stock transactions, including the symbols, shares, prices, and timestamps.

- Logout: Log out of the current user account.

### **Present Issues**:

- Expired API Key: If the IEX Cloud API key used by the application has expired or is no longer valid, users may encounter an error when accessing the homepage. They will be prompted to renew the API key.
- Input Validation: The application may accept invalid or incorrect inputs in certain cases. For example, no extensive testing was done on stock symbol validation as the API is very large.

### **Future Plans**:
- Improved Error Handling: Enhance the error handling mechanism to provide more informative and user-friendly error messages when issues occur during user interactions or API requests.
- Additional Features: Implement new features such as portfolio management, real-time stock charts, and news integration to provide users with a more comprehensive stock trading experience.
- Overhaul the symbol lookup system and change the API from IEX Cloud to Yahoo Finance instead.

### **Contributing**:
Contributions to the project are welcome and encouraged! If you find any issues or have suggestions for improvement, please open an issue or submit a pull request.

### **License**:
The finance web application is open-source and released under the MIT License. You are free to use, modify, and distribute the code according to the terms of the license.
