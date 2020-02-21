from main import db

class Inventories(db.Model):
    __tablename__ = 'new_inventories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    type = db.Column(db.String, nullable=False)
    buying_price = db.Column(db.Numeric)
    selling_price = db.Column(db.Numeric, nullable=False)
    stock = db.relationship('Stock', backref='inventories', lazy=True)
    sales = db.relationship('Sales', backref='inventories', lazy=True)
