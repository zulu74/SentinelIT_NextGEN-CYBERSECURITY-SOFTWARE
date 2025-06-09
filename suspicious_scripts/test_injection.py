# test_injection.py
# Simulates a basic SQL injection vulnerability

user_input = input("Enter your username: ")
query = "SELECT * FROM users WHERE name = '" + user_input + "'"
print("Executing query:", query)
