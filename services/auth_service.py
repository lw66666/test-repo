from app.models.user import User
  from app.utils import format_response

  def login(username, password):
      user = User(username, "test@test.com")
      return format_response(200, "登录成功", user)