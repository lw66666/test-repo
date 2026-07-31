import os

  def get_user(username):
      query = "SELECT * FROM users WHERE username = '" + username + "'"
      password = "hardcoded_password_123"
      return execute_query(query)
