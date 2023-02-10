from datetime import datetime
from flask import Flask, request
import json
from flask_sqlalchemy import SQLAlchemy
import raw_data

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///:memory:'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


def get_response(data:dict) -> json:
    return json.dumps(data), 200, {'Content Type': 'application/json; charset=utf-8'}


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name =db.Column(db.String(100))
    last_name =db.Column(db.String(100))
    age =db.Column(db.Integer)
    email =db.Column(db.String(100))
    role =db.Column(db.String(100))
    phone =db.Column(db.String(100))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}



class Offer(db.Model):
    __tablename__ = "offer"
    id = db.Column(db.Integer, primary_key=True)
    order_id =db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id =db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('offer.id'))
    # customer = db.relationship("User")
    # executor = db.

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


with app.app_context():
    db.create_all()

    for usr_data in raw_data.users:
        db.session.add(User(**usr_data))
        db.session.commit()

    for ord_data in raw_data.orders:
        ord_data['start_date'] = datetime.strptime(ord_data['start_date'], '%m/%d/%Y').date()
        ord_data['end_date'] = datetime.strptime(ord_data['end_date'], '%m/%d/%Y').date()
        db.session.add(Order(**ord_data))
        db.session.commit()

    # ---------Другой вариант записи---------
    # for usr_data in raw_data.users:
    #     new_usr = User(**usr_data)
    #     db.session.add(new_usr)
    #     db.session.commit()
    #
    # for ord_data in raw_data.orders:
    #     ord_data['start_date'] = datetime.strptime(ord_data['start_date'], '%m/%d/%Y').date()
    #     ord_data['end_date'] = datetime.strptime(ord_data['end_date'], '%m/%d/%Y').date()
    #     new_ord = Order(**ord_data)
    #     db.session.add(new_ord)
    #     db.session.commit()

    for ofr_data in raw_data.offers:
        db.session.add(Offer(**ofr_data))
        db.session.commit()


@app.route('/users', methods=['GET','POST'])
def users():
    if request.method == 'GET':
        users = User.query.all()
        result = [user.to_dict() for user in users]
        return get_response(result)

    elif request.method == 'POST':
        user_data = json.loads(request.data)
        db.session.add(User(**user_data))
        db.session.commit()
        return '', 201



@app.route('/users/<int:uid>', methods=['GET','PUT','DELETE'])
def user(uid:int):
    if request.method == 'GET':
        user = User.query.get(uid).to_dict()
        return get_response(user)

    if request.method == 'DELETE':
        user = User.query.get(uid).to_dict()
        db.session.delete(user)
        db.session.commit()
        return '', 204

    if request.method == 'PUT':
        user_data = json.loads(request.data)
        user = User.query.get(uid)
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.age = user_data['age']
        user.email = user_data['email']
        user.role = user_data['role']
        user.phone = user_data['phone']
        # db.session.add(user)
        # db.session.commit()
        return '', 204


@app.route('/orders', methods=['GET','POST'])
def orders():
    if request.method == 'GET':
        orders = Order.query.all()
        result = []
        for order in orders:
            order_dict = order.to_dict()
            order_dict['start_date'] = str(order_dict['start_date'])
            order_dict['end_date'] = str(order_dict['end_date'])
            result.append(order_dict)
        return get_response(result)

    elif request.method == 'POST':
        ord_data = json.loads(request.data)
        db.session.add(User(**ord_data))
        db.session.commit()
        return '', 201



@app.route('/orders/<int:uid>', methods=['GET','PUT','DELETE'])
def order(uid:int):
    if request.method == 'GET':
        order = Order.query.get(uid)
        order_dict = order.to_dict()
        order_dict['start_date'] = str(order_dict['start_date'])
        order_dict['end_date'] = str(order_dict['end_date'])
        return get_response(order_dict)

    if request.method == 'DELETE':
        order = Order.query.get(uid)
        db.session.delete(order)
        db.session.commit()
        return '', 204

    if request.method == 'PUT':
        ord_data = json.loads(request.data)
        ord_data['start_date'] = datetime.strptime(ord_data['start_date'], '%Y-%m-%d').date()
        ord_data['end_date'] = datetime.strptime(ord_data['end_date'], '%Y-%m-%d').date()
        order = Order.query.get(uid)
        order.name = ord_data['name']
        order.description = ord_data['description']
        order.start_date = ord_data['start_date']
        order.end_date = ord_data['end_date']
        order.address = ord_data['address']
        order.price = ord_data['price']
        order.customer_id = ord_data['customer_id']
        order.executor_id = ord_data['executor_id']
        db.session.add(order)
        db.session.commit()
        return '', 204


@app.route('/offers', methods=['GET','POST'])
def offers():
    if request.method == 'GET':
        offers = Offer.query.all()
        result = [offer.to_dict() for offer in offers]
        return get_response(result)

    elif request.method == 'POST':
        ofr_data = json.loads(request.data)
        db.session.add(User(**ofr_data))
        db.session.commit()
        return '', 201



@app.route('/offers/<int:uid>', methods=['GET','PUT','DELETE'])
def offer(uid:int):
    if request.method == 'GET':
        offer = Offer.query.get(uid).to_dict()
        return get_response(offer)

    if request.method == 'DELETE':
        offer = Offer.query.get(uid)
        db.session.delete(offer)
        db.session.commit()
        return '', 204

    if request.method == 'PUT':
        ofr_data = json.loads(request.data)
        offer = Offer.query.get(uid)
        offer.order_id = ofr_data['order_id']
        offer.executor_id = ofr_data['executor_id']
        db.session.add(offer)
        db.session.commit()
        return '', 204

if __name__ == '__main__':
    app.run(debug=True)
