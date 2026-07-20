def format_response(code, message, data=None):
      return {"code": code, "message": message, "data": data}

  def validate_email(email):
      return "@" in email