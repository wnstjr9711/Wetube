from flask import Flask, render_template
import pymysql

app = Flask(__name__)


@app.route('/wnstjr')
def hello_world():
    return render_template('wnstjr.html', data1='김준석', data2='용산', data3=['연희', '연남'])


@app.route('/<user_define>')
def user(user_define):
    return user_define


@app.route('/db')
def show_db():
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1103', db='service', charset='utf8')
    cursor = db.cursor()
    sql = "Select * from test"
    cursor.execute(sql)
    result = str(cursor.fetchall())
    db.close()
    return result


@app.route('/')
def home():
    return render_template('html/home/index.html')


@app.route('/movies')
def movie():
    return render_template('html/single-video/single-video-v1.html')


if __name__ == '__main__':
    app.run(debug=True)
