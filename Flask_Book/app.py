from flask import Flask,render_template,request,flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField
from wtforms.validators import DataRequired,EqualTo
app = Flask(__name__)

'''
1、配置数据库
2、添加书和作者模型
3、添加数据

4、使用模板显示数据库查询数据
a.查询所有作者信息，让信息传递给模板
b.模板中按照格式，依次循环出作者，他的所有书籍（作者获取书籍，用的是关系引用）


5、使用wtf表单
a.自定义表单类
b.模板中显示
c.secret_key=''
d.编码格式
e.模板中 跨域问题 csrf_token

6、实现相关的增删逻辑
a.增加数据
b.删除数据--》网页中删除，--》点击需要发送的书籍id给删除书籍的路由
'''

#配置数据库
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:123456@127.0.0.1/flask_book' #配置数据库的地址
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False  #动态跟踪，不建议开启

# -*- coding:utf-8 -*-
import importlib,sys
importlib.reload(sys)


app.secret_key='123'
db=SQLAlchemy(app)  #创建数据对象


#定义书和作者的模型

class Author(db.Model):  #作者模型
    __tablename__ = 'authors' #表名

    #字段
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)

    #关系引用
    books=db.relationship('Book',backref='author') #books是给自己用的，author是给Book用的

    def __repr__(self): #repr()显示一个可读的字符串
        return 'Author:%s' %self.name


class Book(db.Model): #书籍模型
    _tablename__ = 'books'  # 表名

    # 字段
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)
    author_id=db.Column(db.Integer,db.ForeignKey('authors.id'))

    def __repr__(self): #repr()显示一个可读的字符串
        return '<Book:%s %s>' %(self.name,self.author_id)



# db.drop_all()  #删除表
# db.create_all()  #创建表
#
# #添加数据
# au1=Author(name='老王')
# au2=Author(name='老惠')
# au3=Author(name='老刘')
#
# db.session.add_all([au1,au2,au3])#把数据提交给用户会话
# db.session.commit() #提交用户会话
#
# bk1=Book(name='老王回忆录',author_id=au1.id)
# bk2=Book(name='我读书少，你别骗我',author_id=au1.id)
# bk3=Book(name='如何才能让自己更骚',author_id=au2.id)
# bk4=Book(name='如何征服美丽少女',author_id=au3.id)
# bk5=Book(name='如何征服熟妇',author_id=au3.id)
#
# db.session.add_all([bk1,bk2,bk3,bk4,bk5])
# db.session.commit()

#自定义表单类
class AuthorForm(FlaskForm):
    author=StringField('作者姓名',validators=[DataRequired()])
    name=StringField('书籍名',validators=[DataRequired()])
    sublimt=SubmitField('提交')


#删除作者
@app.route('/delete_author/<author_id>')
def delete_author(author_id):
    #查询数据库是否有该Id的书，如果有就删除(先删除书，再删除作者），如果没有就提示没有
    author=Author.query.get(author_id)

    #如果有就删除(先删除书，再删除作者)
    if author:
        try:
            #查询之后直接删除
            Book.query.filter_by(author_id=author.id).delete()

            #删除作者
            db.session.delete(author)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除作者失败')
            db.session.rollback()
        #如果没有就提示没有
    else:
        flash('作者找不到')


    return redirect(url_for('index'))


#删除书籍
@app.route('/delete_book/<book_id>')
def delete_book(book_id):
    #查询数据库是否有该Id的书，如果有就删除，如果没有就提示没有
    book=Book.query.get(book_id)

    #如果有就删除
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除书籍失败')
            db.session.rollback()
        #如果没有就提示没有
        else:
            flash('书籍找不到')


    #返回当前网址 ---> 重定向
    return redirect(url_for('index')) #redirect：重定向，需要传入网址，或者路由地址    #加上url_for 可以写入函数名，返回该函数的路由地址

    pass




#增加数据
@app.route('/',methods=['GET','POST'])
def index():

    author_form=AuthorForm() #创建表单类对象

    '''
    验证逻辑
    1、调用wtf的验证函数
    2、验证通过获取数据
    3、判断作者是否存在，
    4、如果作者存在判断书籍是否存在，如果没有重复书籍就添加数据，如果重复就提示错误
    5、如果作者不存在就添加作者和书籍
    6、如果验证不通过，就提示错误
    '''
    #1、调用wtf的验证函数
    if author_form.validate_on_submit():
        #2、验证通过获取数据
        author_name=author_form.author.data
        book_name=author_form.name.data
        #3、判断作者是否存在
        author=Author.query.filter_by(name=author_name).first()
        #4、如果作者存在判断书籍是否存在
        if author:
            #判断书籍是否存在
            book=Book.query.filter_by(name=book_name).first()
            #如果重复就提示错误
            if book:
                flash('已存在')
            #如果没有重复书籍就添加数据，
            else:
                try:
                    new_book=Book(name=book_name,author_id=author.id)
                    db.session.add(new_book)
                    db.session.commit()
                except Exception as e:
                    print(e)
                    flash('添加书籍失败')


            pass
        else:
            #5、如果作者不存在就添加作者和书籍
            try:
                new_author=Author(name=author_name)
                db.session.add(new_author)
                db.session.commit()

                new_book = Book(name=book_name, author_id=new_author.id)
                db.session.add(new_book)
                db.session.commit()
            except Exception as e:
                print(e)
                flash('添加失败')
                db.session.rollback()

            pass


        pass
    else:
        #6、如果验证不通过，就提示错误
        if request.method =='POST':
            flash('参数不全')

    authors = Author.query.all()  # 查询所有作者的信息，让信息传递给模板
    return render_template('books.html',authors=authors,author_form=author_form)



if __name__ == '__main__':
    app.run(debug=True)
