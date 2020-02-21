from flask import Flask, render_template, request, redirect, url_for, flash
import pygal
import psycopg2
import datetime
from Config.Config import Development

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app.config.from_object(Development)
app.config['SQLALCHEMY_DATABASE_URI']= 'postgresql://postgres:Leon@1996@127.0.0.1:5432/classjan'
db = SQLAlchemy(app)


class Inventories(db.Model):
    __tablename__ = 'new_inventories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    type = db.Column(db.String, nullable=False)
    buying_price = db.Column(db.Numeric)
    selling_price = db.Column(db.Numeric, nullable=False)
    stock = db.relationship('Stock', backref='inventories', lazy=True)
    sales = db.relationship('Sales', backref='inventories', lazy=True)

class Stock(db.Model):
    __tablename__='new_stock'
    id = db.Column(db.Integer, primary_key=True)
    inv_id = db.Column(db.Integer, db.ForeignKey('new_inventories.id'))
    stock = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Sales(db.Model):
    __tablename__='new_sales'
    id = db.Column(db.Integer, primary_key=True)
    inv_id = db.Column(db.Integer, db.ForeignKey('new_inventories.id'))
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/adding/<x>/<y>')
def addition(x,y):
    return str(int(x)+int(y))


@app.route('/person/<name>/<int:age>')
def person(name, age):
    return f'{name} is {age} Years old'.upper()


@app.route('/add/<int:x>/<int:y>')
def add(x,y):
    total = x+y
    return f'Sum of {x} and {y} is {total}'

conn = psycopg2.connect("dbname='classjan' user='postgres' host='localhost' password='Leon@1996'")

cur = conn.cursor()



@app.route('/')
def index():

    data =[('Internet Explorer', 19.5),
           ('Firefox', 36.6),
           ('Chrome', 36.3),
           ('Safari', 4.5),
           ('Opera', 2.3)
           ]

    pie_chart = pygal.Pie()
    pie_chart.title = "Browser usage in February 2012 (in %)"
    pie_chart.add(data[0][0], data[0][1])
    pie_chart.add(data[1][0], data[1][1])
    pie_chart.add(data[2][0], data[2][1])
    pie_chart.add(data[3][0], data[3][1])
    pie_chart.add(data[4][0], data[4][1])

    pie_data = pie_chart.render_data_uri()

    data_line = [('January', 20),
                 ('Febuary', 40),
                 ('March', 31),
                 ('April', 82),
                 ('May', 60),
                 ('June', 13),
                 ('July', 17),
                 ('August', 35),
                 ('September', 55),
                 ('October', 82),
                 ('November', 79),
                 ('December', 40)
                 ]

    cur.execute("""SELECT sum(s.s_qty) as subtotal,
    EXTRACT(MONTH FROM s.time_created) as sales_month
    from sales as s
    join inventories as i on s.inv_id = i.id
    GROUP BY sales_month
    ORDER BY sales_month""")

    records = cur.fetchall()

    x = []
    sales = []
    for i in records:
        x.append(i[1])
        sales.append(i[0])
        # print(i[0])

    print(x)
    print(sales)

    line_chart = pygal.Line()
    line_chart.title = 'Sales for the year 2019'
    line_chart.x_labels = map(str, x)
    line_chart.add('Sales', sales)
    # line_chart.add('Chrome', [None, None, None, None, None, None, 0, 3.9, 10.8, 23.8, 35.3])
    # line_chart.add('IE', [85.8, 84.6, 84.7, 74.5, 66, 58.6, 54.7, 44.8, 36.2, 26.6, 20.1])
    # line_chart.add('Others', [14.2, 15.4, 15.3, 8.9, 9, 10.4, 8.9, 5.8, 6.7, 6.8, 7.5])
    line_data = line_chart.render_data_uri()

    return render_template('index.html', pie_data = pie_data, line_data = line_data)


@app.route('/inventories', methods=['GET','POST'])
def inventories():
    # check if the request is a post

    r = Inventories.query.all()


    cur.execute("""SELECT inv_id, sum(quantity) as "stock"
	FROM ((SELECT st.inv_id, sum(stock) as "quantity"
	FROM public.new_stock as st
	GROUP BY inv_id) union all
		 (SELECT sa.inv_id, - sum(quantity) as "quantity"
	FROM public.new_sales as sa
	GROUP BY inv_id) 
		 ) stsa
	GROUP BY inv_id
	ORDER BY inv_id;""")

    remStock = cur.fetchall()
    for each in remStock:
        print(each[1])

    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']
        bp = request.form['buying_price']
        sp = request.form['selling_price']

        record = Inventories(name=name, type=type, buying_price=bp,selling_price=sp)
        db.session.add(record)
        db.session.commit()
        #
        # flash('You were successfully logged in')

        return redirect(url_for('inventories'))

    return render_template('inventories.html', records = r, remStock = remStock)

# @app.route('/inventories', methods=['POST'])
# def send_inv():
#     return render_template('inventories.html')



@app.route('/add_stock/<inv_id>', methods=['GET','POST'])
def add_stock(inv_id):
    if request.method == 'POST':
        # print(inv_id)
        stock = request.form['stock']

        stock = Stock(inv_id=inv_id, stock=stock)
        db.session.add(stock)
        db.session.commit()
        # print(stock)

    return redirect(url_for('inventories'))


@app.route('/make_sale/<inv_id>', methods=['GET','POST'])
def make_sale(inv_id):
    if request.method == 'POST':
        # print(inv_id)
        total = request.form['quantity']
        sale = Sales(inv_id=inv_id, quantity=total)
        db.session.add(sale)
        db.session.commit()
    return redirect(url_for('inventories'))


if __name__ == '__main__':
    app.run()
