import mysql.connector

mydb = mysql.connector.connect(
  host='localhost',
  user='root',
  password='H=o%0Nv6',
  database='schemadb'
)

if mydb.is_connected():
    print("connection established......")
    print("Connection id : ", mydb.connection_id)


# create cursor object
cursor = mydb.cursor()

def customer(id):
    while True:
        print("Press 1 to view profile and other information")
        print("Press 2 to Check Cart")
        print("Press 3 to Add medicines to cart")
        print("Press 4 to View previous review or Add new review")
        print("Press 5 to Update Membership")
        print("Press 6 to Add Money to account")        
        print("Press 7 to Logout")
        user_type = int(input())

        if user_type == 1:
            sql = "SELECT * FROM Customer WHERE CustomerID = %s "
            cursor.execute(sql, (id,))
            result = cursor.fetchone()
            print("Customer ID =", result[0])
            print("Name =", result[1])
            print("Phone Number =", result[2])
            print("Email =", result[3])
            print("Password =", result[4])
            print("Address =", result[5])
            print("Customer Type =", result[6])
            print("Wallet Balance =", result[7])

        elif user_type == 2:
          while True:
              print("Press 1 to view cart Total Bill")
              print("Press 2 to Clear cart")
              print("Press 3 to Checkout and Order")
              print("Press 4 to return to main menu")
              cart_option = int(input())
              
              if cart_option == 1:
                  sql = "SELECT * FROM Cart WHERE Customer_ID = %s "
                  cursor.execute(sql, (id,))
                  result = cursor.fetchone()
                  print("Cart Total bill =", result[2])
              
              elif cart_option == 2:
                  sql = "DELETE FROM Cart_Items WHERE Cart_ID IN (SELECT CartID FROM Cart WHERE Customer_ID = %s);"
                  cursor.execute(sql, (id,))
                  sql = "UPDATE Cart SET Total_Bill = 0 WHERE Customer_ID = %s;"
                  cursor.execute(sql, (id,))
                  print("Cart has been cleared!")
              
              elif cart_option == 3:
                  # get the cart total bill for the customer
                  sql = "SELECT Total_Bill FROM Cart WHERE Customer_ID = %s"
                  cursor.execute(sql, (id,))
                  total_bill = cursor.fetchone()[0]

                  # check if the customer has sufficient wallet balance to pay the bill
                  sql = "SELECT Wallet_Balance FROM Customer WHERE CustomerID = %s"
                  cursor.execute(sql, (id,))
                  wallet_balance = cursor.fetchone()[0]
                  if wallet_balance < total_bill:
                      print("Insufficient wallet balance!")
                  else:
                      # update the customer's wallet balance and deduct the bill amount
                      new_wallet_balance = wallet_balance - total_bill
                      sql = "UPDATE Customer SET Wallet_Balance = %s WHERE CustomerID = %s"
                      cursor.execute(sql, (new_wallet_balance, id))

                      # create a new order for the customer
                      sql = "INSERT INTO Orders (Customer_ID, Total_Bill) VALUES (%s, %s)"
                      cursor.execute(sql, (id, total_bill))
                      order_id = cursor.lastrowid

                      # move the items from the cart to the order_items table
                      sql = "SELECT Medicine_ID, Quantity, Price FROM Cart_Items WHERE Cart_ID IN (SELECT CartID FROM Cart WHERE Customer_ID = %s)"
                      cursor.execute(sql, (id,))
                      cart_items = cursor.fetchall()
                      for item in cart_items:
                          medicine_id, quantity, price = item
                          sql = "INSERT INTO Order_Items (Order_ID, Medicine_ID, Quantity, Price) VALUES (%s, %s, %s, %s)"
                          cursor.execute(sql, (order_id, medicine_id, quantity, price))
                      sql = "DELETE FROM Cart_Items WHERE Cart_ID IN (SELECT CartID FROM Cart WHERE Customer_ID = %s);"
                      cursor.execute(sql, (id,))
                      sql = "UPDATE Cart SET Total_Bill = 0 WHERE Customer_ID = %s;"
                      cursor.execute(sql, (id,))
                      print("Order placed successfully!")
              
              elif cart_option == 4:
                  break
              
              else:
                  print("Invalid option. Please try again.")

                            

        elif user_type == 3:
          while True:
              medicine_name = input("Enter medicine name: ")
              # query the Medicine table to check if the medicine exists
              query = "SELECT Price FROM Medicine WHERE Name = %s"
              cursor.execute(query, (medicine_name,))
              result = cursor.fetchone()

              # if medicine exists, update the cart total bill
              if result:
                  price = result[0]
                  cart_id = id  # assume the cart id is 1 for demonstration purposes
                  update_query = "UPDATE Cart SET Total_Bill = Total_Bill + %s WHERE CartID = %s"
                  cursor.execute(update_query, (price, cart_id))
                  mydb.commit()
                  print(f"{medicine_name} added to cart. Total bill updated.")
              else:
                  print(f"{medicine_name} not found in Medicine table.")
                  
              more_items = input("Add more items to cart? (y/n): ")
              if more_items.lower() == "n":
                  break
         # If the user selects option 4, show them their previous reviews and allow them to add a new one
        if user_type == 4:
            # Use a SELECT statement to get the customer's previous reviews
            cursor.execute("SELECT Review_Text, Date_and_Time FROM Review WHERE Customer_ID = %s", (id,))
            result = cursor.fetchall()

            # If the customer has no previous reviews, let them know
            if not result:
                print("You haven't written any reviews yet.")
            else:
                # Print out the customer's previous reviews
                for review in result:
                    print(review[0], "- Written on", review[1])

            # Ask the customer if they want to add a new review
            print("Do you want to add a new review? (Y/N)")
            answer = input()

            if answer.lower() == "y":
                # Ask the customer for their new review
                print("Enter your new review:")
                new_review = input()

                # Insert the new review into the database
                sql = "INSERT INTO Review (Review_Text, Date_and_Time, Customer_ID) VALUES (%s, NOW(), %s)"
                val = (new_review, id)
                cursor.execute(sql, val)
                mydb.commit()

                print("Review added successfully.")      
        # If the user selects option 5, allow them to update their membership status
        elif user_type == 5:
            # Print out the available membership options
            print("Select your new membership status:")
            print("1. Silver")
            print("2. Gold")
            print("3. Platinum")
            print("4. Diamond")

            # Ask the customer for their new membership status
            new_membership = int(input())

            # Use a switch statement to update the customer's membership status based on their input
            if new_membership == 1:
                new_status = "Silver"
                membership_charge = 0
            elif new_membership == 2:
                new_status = "Gold"
                membership_charge = 100
            elif new_membership == 3:
                new_status = "Platinum"
                membership_charge = 200
            elif new_membership == 4:
                new_status = "Diamond"
                membership_charge = 300
            else:
                print("Invalid input. Membership status not updated.")
                continue

            # Check if the customer has enough balance in their wallet to pay for the membership upgrade
            cursor.execute("SELECT Wallet_Balance FROM Customer WHERE CustomerID = %s", (id,))
            result = cursor.fetchone()
            wallet_balance = result[0]

            if wallet_balance < membership_charge:
                print("Insufficient balance. Please add funds to your wallet.")
                continue

            # Update the customer's membership status and deduct the charge from their wallet balance
            sql = "UPDATE Customer SET Customer_Type = %s, Wallet_Balance = Wallet_Balance - %s WHERE CustomerID = %s"
            val = (new_status, membership_charge, id)
            cursor.execute(sql, val)
            mydb.commit()

            print("Membership status updated successfully.")
            print(f"{membership_charge} credits have been deducted from your wallet balance. Your new balance is {wallet_balance - membership_charge} credits.")
        elif user_type == 6:
                        email = input("Enter your email address: ")
                        password = input("Enter your password: ")
                        amount = int(input("Enter the amount to add: "))

                        # Check if email and password are correct
                        cursor.execute("SELECT * FROM Customer WHERE CustomerID = %s AND Email_Id = %s AND Password = %s", (id, email, password))
                        result = cursor.fetchone()

                        if result:
                            # Update wallet balance
                            new_balance = result[7] + amount
                            cursor.execute("UPDATE Customer SET Wallet_Balance = %s WHERE CustomerID = %s", (new_balance, id))
                            mydb.commit()

                            print("Wallet balance updated successfully. New balance: ", new_balance)
                        else:
                            print("Invalid email or password.")
        elif user_type == 7:
            print("Logging out...")
            break

        else:
            print("Unexpected Input")

    
def manager(id):
    while True:
        print("Press 1 to view profile and other information")
        print("Press 2 to Manage delivery Person")
        print("Press 3 to Manage medicines ")
        print("Press 4 to Manage Customer")
        print("Press 5 to Manage employees ")
        print("Press 6 to Manage Manufacturer")        
        print("Press 7 to exit ")
        user_type = int(input())

        if user_type == 1:
            sql = "SELECT * FROM Manager WHERE ManagerID = %s "
            cursor.execute(sql, (id,))
            result = cursor.fetchone()
            print("Manager ID =", result[0])
            print("Name =", result[1])
            print("BranchId =", result[2])
            print("Age =", result[3])
            print("email =", result[4])
            

        elif user_type == 2:
          while True:
              print("Press 1 to view Delivery Person detail :")
              print("Press 2 to Delete Delivery Person detail :")
              print("Press 3 to return to main menu :")
              cart_option = int(input())
              
              if cart_option == 1:
                  x=int(input("Enter Delivery Partner ID :"))
                  sql = "SELECT * FROM Delivery_Partner  WHERE PersonID = %s "
                  cursor.execute(sql, (x,))
                  result = cursor.fetchone()
                  print("Delivery Person ID =", result[0])
                  print("Name: =", result[1])
                  print("Date_of_joining =", result[2])
                  print("EmailId =", result[3])
                  print("Branch =", result[4])
                 
              elif cart_option == 2:
                  x=int(input("Enter Delivery Partner ID :"))
                  sql = "DELETE FROM Delivery_Partner WHERE PersonID = %s;"
                  cursor.execute(sql, (x,))
                  mydb.commit() 
                  print("Delivery Person deleted")
              
              elif cart_option == 3:
                  break
              
              else:
                  print("Invalid option. Please try again.")

                            

        elif user_type == 3:
          while True:
              print("Press 1 to add a new medicine:")
              print("Press 2 to get medicine detail")
              print("Press 3 to delete a medicine :")
              print("Press 4 to edit the medicine price:")
              print("Press 5 to return to main menu:")
              x=int(input())
              if x==1:
                name = input("Enter the name of the medicine: ")
                manufacture_date = input("Enter the date of manufacture (YYYY-MM-DD): ")
                expiry_date = input("Enter the date of expiry (YYYY-MM-DD): ")
                manufacturer_name = input("Enter the name of the manufacturer: ")
                price = float(input("Enter the price of the medicine: "))
                description = input("Enter a description of the medicine: ")

                # Create an SQL INSERT query
                sql = "INSERT INTO medicine (Name, Date_of_manufacture, Date_of_expiry, Manufacturer_Name, Price, Description) VALUES (%s, %s, %s, %s, %s, %s)"
                values = (name, manufacture_date, expiry_date, manufacturer_name, price, description)

                # Execute the SQL query with the user-provided values
                cursor.execute(sql, values)

                # Commit the changes to the database and close the cursor and database connection
                mydb.commit()
                print("Medicine added ")
              elif x==2:
                    y=int(input("Enter Medicine ID:"))
                    sql = "SELECT * FROM medicine  WHERE MedicineID = %s "
                    cursor.execute(sql, (y,))
                    result = cursor.fetchone()
                    print("Medicine ID =", result[0])
                    print("Name: =", result[1])
                    print("Date_of_jManufacture =", result[2])
                    print("Date_of_Expiry =", result[3])
                    print("Manufacturer Name =", result[4])
                    print("Price =", result[5])
                    print("Description =", result[6])
              elif x==3:
                  y=int(input("Enter Medicine ID :"))
                  sql = "DELETE FROM medicine WHERE MedicineID = %s;"
                  cursor.execute(sql, (y,))
                  mydb.commit() 
                  print("Medicine  deleted")
              elif x==4:
                  y=int(input("Enter Medicine ID :"))
                  z=int(input("Enter Medicine new price :"))
                  sql = "UPDATE medicine SET Price = %s WHERE MedicineID = %s"
                  values = (y,z)
                  cursor.execute(sql, values)
                  mydb.commit()
                  print("medicine updated")
              elif x==5:
                  break
              else:
                  print("Invalid option. Please try again.")
         # If the user selects option 4, show them their previous reviews and allow them to add a new one
        if user_type == 4:
            while True:
              print("Press 1 to  view a customer:")
              print("Press 2 to delete a customer :")
              print("Press 3 to return to main menu :")
              x=int(input())
              if x==1:
                    y=int(input("Enter Customer ID :"))
                    sql = "SELECT * FROM customer  WHERE CustomerID = %s "
                    cursor.execute(sql, (y,))
                    result = cursor.fetchone()
                    print("Customer ID =", result[0])
                    print("Name: =", result[1])
                    print("Phone Number =", result[2])
                    print("Email id =", result[3])
                    print("password =", result[4])
                    print("Address =", result[5])
                    print("Customer type =", result[6])
                    print("Wallet Balance =", result[7])
              elif x==2:
                  y=int(input("Enter Customer ID :"))
                  review_sql = "DELETE FROM review WHERE Customer_ID = %s"
                  cursor.execute(review_sql, (y,))
                  sql = "DELETE FROM customer  WHERE CustomerID = %s;"
                  cursor.execute(sql, (y,))
                  mydb.commit() 
                  print("Customer  deleted")
              elif x==3:
                  break
              else:
                  print("Invalid option. Please try again.")
        # If the user selects option 5, allow them to update their membership status
        elif user_type == 5:
            while True:
              print("Press 1 to  view an Employee:")
              print("Press 2 to  add an Employee:")
              print("Press 3 to delete an Employee :")
              print("Press 4 to return to main menu :")
              x=int(input())
              if x==1:
                    y=int(input("Enter Customer ID :"))
                    sql = "SELECT * FROM employee  WHERE EmployeeID = %s "
                    cursor.execute(sql, (y,))
                    result = cursor.fetchone()
                    print("Employee ID =", result[0])
                    print("Name: =", result[1])
                    print("Date of Joining =", result[2])
                    print("Email id =", result[4])
                    print("Age =", result[3])
                    print("BranchID =", result[5])
                    print("Department ID =", result[6])
                    
              elif x==2:
                name = input("Enter the employee's name: ")
                date_of_joining = input("Enter the date of joining (YYYY-MM-DD): ")
                age = int(input("Enter the employee's age: "))
                email = input("Enter the employee's email ID: ")
                branch_id = int(input("Enter the employee's branch ID: "))
                department_id = int(input("Enter the employee's department ID: "))
                dependent_id = int(input("Enter the employee's dependent ID: "))

                # Insert the employee details into the employee table
                sql = "INSERT INTO employee (Name, Date_of_joining, Age, Email_ID, BranchID, Department_ID, Dependent_ID) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                values = (name, date_of_joining, age, email, branch_id, department_id, dependent_id)
                cursor.execute(sql, values)

                # Commit the changes to the database and close the cursor and database connection
                mydb.commit()
                print("Employee added")
              elif x==3:
                  y=int(input("Enter Employee ID:"))
                  sql = "DELETE FROM employee  WHERE EmployeeID = %s;"
                  cursor.execute(sql, (y,))
                  mydb.commit() 
                  print("Employee  deleted")

              elif x==4:
                  break
              else:
                  print("Invalid option. Please try again.")
        elif user_type == 6:
             while True:
              print("Press 1 to  view a Manufacturer:")
              print("Press 2 to  add a Manufacturer:")
              
              print("Press 3 to return to main menu :")
              x=int(input())
              if x==1:
                    y=int(input("Enter Manufacturer ID :"))
                    sql = "SELECT * FROM manufacturer  WHERE ManufacturerID = %s "
                    cursor.execute(sql, (y,))
                    result = cursor.fetchone()
                    print("Manufacturer ID =", result[0])
                    print("Name: =", result[1])
                    print("Phone Number =", result[2])
                    print("Address =", result[3])
                    
              elif x==2:
                name = input("Enter the Manufacturer's name: ")
                date_of_joining = input("Phone Number")
                age = input("Address:")
                # Insert the employee details into the employee table
                sql = "INSERT INTO manufacturer (Name, Phone_Number, Address ) VALUES (%s, %s, %s)"
                values = (name, date_of_joining, age)
                cursor.execute(sql, values)

                # Commit the changes to the database and close the cursor and database connection
                mydb.commit()
                print("Manufacturer added")
              

              elif x==3:
                  break
              else:
                  print("Invalid option. Please try again.")
            
        elif user_type == 7:
            print("Logging out...")
            break

        else:
            print("Unexpected Input")

        
# function to register a new customer
def register_customer(name, phone, email, password, address, wallet_balance):
    sql = "INSERT INTO Customer (Name, Phone_Number, Email_Id, password, Address, Wallet_Balance) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (name, phone, email, password, address, wallet_balance)
    cursor.execute(sql, val)
    mydb.commit()
    print("New customer registered with ID:", cursor.lastrowid)

    # create a new cart for the customer with total bill as 0
    cart_sql = "INSERT INTO Cart (Customer_ID) VALUES (%s)"
    cart_val = (cursor.lastrowid,)
    cursor.execute(cart_sql, cart_val)
    mydb.commit()
    print("Cart created for customer with ID:", cursor.lastrowid)

    print("Please Login To continue with Gopharma")
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    login_customer(email, password)


# function to login as a customer
def login_customer(email, password):
    sql = "SELECT * FROM Customer WHERE Email_Id = %s AND password = %s"
    val = (email, password)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    if result:
        print("Welcome", result[1])
        customer(result[0])
    else:
        print("Invalid email or password")

# function to register a new manager
def register_manager(name, branch_id, age, email, password):
    sql = "INSERT INTO Manager (Manager_Name, BranchId, Age, Email, password) VALUES (%s, %s, %s, %s, %s)"
    val = (name, branch_id, age, email, password)
    cursor.execute(sql, val)
    mydb.commit()
    print("New manager registered with ID:", cursor.lastrowid)
    print("Please Login To continue with Gopharma")
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    login_manager(email, password)


# function to login as a manager
def login_manager(email, password):
    sql = "SELECT * FROM Manager WHERE Email = %s AND Password = %s"
    val = (email, password)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    if result:
        print("Welcome", result[1])
        manager(result[0])
    else:
        print("Invalid email or password")

print("*****************************************WELCOME TO GOPHARMA******************************************")
while True:
    user_type = input("Are you a customer or a manager? Type 'c' for customer, 'm' for manager: ")
    if user_type == 'c':
        action = input("Type 'l' to login or 's' to signup: ")
        if action == 'l':
            email = input("Enter your email: ")
            password = input("Enter your password: ")
            login_customer(email, password)
            break
        elif action == 's':
            name = input("Enter your name: ")
            phone = input("Enter your phone number: ")
            email = input("Enter your email: ")
            password = input("Enter your password: ")
            address = input("Enter your address: ")
            wallet_balance = int(input("Enter your wallet balance (must be at least 50): "))
            register_customer(name, phone, email, password, address, wallet_balance)
            break
        else:
            print("Invalid action. Try again.")
    elif user_type == 'm':
        action = input("Type 'l' to login or 's' to signup: ")
        if action == 'l':
            email = input("Enter your email: ")
            password = input("Enter your password: ")
            login_manager(email, password)
            break
        elif action == 's':
            name = input("Enter your name: ")
            branch_id = int(input("Enter your branch ID: "))
            age = int(input("Enter your age: "))
            email = input("Enter your email: ")
            password = input("Enter your password: ")
            register_manager(name, branch_id, age, email, password)
            break
        else:
            print("Invalid action. Try again.")   

mydb.commit() # Commit all the transactions


mydb.close()
