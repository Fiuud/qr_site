from flask import Flask, render_template, request, redirect, url_for
from flask_qrcode import QRcode
from flask_mysqldb import MySQL
import MySQLdb

app = Flask(__name__)
QRcode(app)
mysql = MySQL(app)

id_lesson = None


# Connect DB
def create_connection():
    connection = None
    try:
        app.config['MYSQL_HOST'] = 'localhost'
        app.config['MYSQL_USER'] = 'root'
        app.config['MYSQL_PASSWORD'] = ''
        app.config['MYSQL_DB'] = 'qr_site'
        app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
        print("Connection to MySQL DB successful")
    except MySQLdb.OperationalError as e:
        print(f'MySQL server has gone away: {e}, trying to reconnect')
        raise e

    return connection


# Read DB
def execute_read_query(query):
    cursor = mysql.connection.cursor()
    result = None
    try:
        cursor.execute(query)
        if cursor.rowcount == 1:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
        return result
    except MySQLdb.OperationalError as e:
        print(f'MySQL server has gone away: {e}, trying to reconnect')
        raise e


# Write DB
def execute_query(query):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute(query)
        mysql.connection.commit()

        ID = cursor.lastrowid
        cursor.close()
        return ID
    except MySQLdb.OperationalError as e:
        print(f'MySQL server has gone away: {e}, trying to reconnect')
        raise e


create_connection()


# Show lesson on page
@app.route('/', methods=['GET', 'POST'])
def check_lessons():

    check_sql = f'''select * from lessons ORDER BY title'''
    data = execute_read_query(check_sql)

    return render_template("index.html", data=data)


# Create lesson
@app.route('/create_lesson', methods=['GET', 'POST'])
def create_lessons():
    if request.method == 'POST':
        title = request.form['title']

        check_sql = f'''insert into Lessons (title) values ({title})'''
        ID = execute_query(check_sql)

        return redirect(url_for('.lessons', id=ID))

    return render_template("create_lesson.html")


# show specific lesson and its lists
@app.route("/lessons/<int:id>", methods=['GET', 'POST'])
def lessons(id):
    global id_lesson
    id_lesson = id
    check_sql = f'''SELECT * FROM lessons WHERE id = {id}'''
    lesson = execute_read_query(check_sql)

    check_sql = f"""SELECT lists.id, lists.date 
    from lessons_has_lists, lessons, lists 
    where lessons.id = lessons_id AND lists.id=lists_id AND lessons_id = {id}"""
    data = execute_read_query(check_sql)
    # if request.method == 'POST':
    #     id_list = request.form['title']

    return render_template('lesson.html', lesson=lesson, lists=data)


@app.route("/lessons/<int:id>/<int:id_lists>", methods=['GET', 'POST'])
def lists(id, id_lists):
    check_sql = f'''SELECT * FROM lists WHERE id = {id_lists}'''
    list_one = execute_read_query(check_sql)

    check_sql = f'''select first_name, last_name, group_concat(distinct date_scan) as date 
    from lists_has_students, students 
    where lists_id = {id_lists} and students.id = lists_has_students.students_id group by students_id'''
    data_students = execute_read_query(check_sql)

    return render_template('lists.html', list_one=list_one, students=data_students)


if __name__ == '__main__':
    app.run(debug=True)
