from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=9, message="用户名长度应在3到9之间。")])
    password = PasswordField('密码', validators=[DataRequired(),Length(min=3, max=9, message="用户名长度应在3到9之间。")])
    submit = SubmitField('登录')

class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=9, message="用户名长度应在3到9之间。")])
    password = PasswordField('密码', validators=[DataRequired(),Length(min=3,max=13, message="密码长度应在3到13之间。")])
    email = StringField('邮箱', validators=[DataRequired(), Email(), Email(message="请输入有效的邮箱地址。")])
    submit = SubmitField('注册')

class CheckoutForm(FlaskForm):
    name = StringField('姓名', validators=[DataRequired(), Length(min=1, max=9, message="姓名长度应在1到9之间。")])
    contact = StringField('联系方式', validators=[DataRequired(),Length(min=1,max=20, message="联系方式长度应在1到20之间。")])
    address = StringField('地址', validators=[DataRequired(),Length(min=1,max=100, message="地址长度应在1到100之间。")])
    submit = SubmitField('提交')

class AddProductForm(FlaskForm):
    name = StringField('商品名称', validators=[DataRequired()])
    description = TextAreaField('商品描述', validators=[DataRequired()])
    price = FloatField('价格', validators=[DataRequired()])
    category = StringField('商品分类', validators=[DataRequired()])
    image = StringField('商品图片URL (Store)', validators=[DataRequired()])
    image2 = StringField('商品图片URL (Product Page)', validators=[DataRequired()])
    stock = IntegerField('库存', validators=[DataRequired()])
    submit = SubmitField('添加商品')
