from app.models.user import User
  from app.utils import format_response

  def get_user(user_id):
      return format_response(200, "success", None)

  def create_user(username, email):
      user = User(username, email)
      return format_response(201, "创建成功", user)