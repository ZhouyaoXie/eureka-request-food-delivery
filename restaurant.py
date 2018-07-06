import pika
import sys
import mysql.connector
from mysql.connector import Error, MySQLConnection
from database import connect, disconnect

def update_order_state(order_id, order_state):
	query="""UPDATE mel_order
	SET order_state = %s
	WHERE order_id= %s"""

	data=(order_state, order_id)

	conn=connect('restaurant')
	cursor=conn.cursor()
	cursor.execute(query, data)
	conn.commit()

	cursor.close()
	disconnect(conn)

	print('Successfully updated order state to', order_state)

#return the restaurant id of an order
def retrieve_re_id(order_id):
	query = """SELECT re_id
	FROM mel_order
	WHERE order_id = %s""" % order_id
	re_id=None

	conn=connect('restaurant')
	cursor=conn.cursor(buffered=True)
	cursor.execute(query)
	for result in cursor.fetchall():
		re_id = result[0]

	cursor.close()
	disconnect(conn)

	return re_id

#return a restaurant's address
def retrieve_re_add(re_id):
	query = """SELECT re_add
	FROM restaurant
	WHERE re_id = %s""" % re_id
	re_add=None

	conn=connect('restaurant')
	cursor=conn.cursor(buffered=True)
	cursor.execute(query)
	for result in cursor.fetchall():
		re_add = result[0]

	cursor.close()
	disconnect(conn)

	return re_add

#return the delivery address of an order
def retrieve_add(order_id):
	query = """SELECT `add`
	FROM mel_order
	WHERE order_id = %s""" % order_id
	add=None

	conn=connect('restaurant')
	cursor=conn.cursor(buffered=True)
	cursor.execute(query)
	for result in cursor.fetchall():
		add = result[0]

	cursor.close()
	conn.close()

	return add

#insert new row into order_delivery table
def create_od(order_id, re_add, add):
	od_id=max_od_id()+1
	od_state=1

	query = """INSERT INTO order_delivery
	VALUES(%s, %s, %s, %s, %s, %s) """
	data=(od_id, order_id, None, od_state, re_add, add)

	conn=connect('restaurant')
	cursor=conn.cursor()
	cursor.execute(query, data)
	conn.commit()

	cursor.close()
	disconnect(conn)

	print('Successfully created new order delivery entry, order_id %s, od_id %s' % (order_id, od_id))
	return od_id

#find the id of the last od inserted.
#assume that od_id starts from 1 and increments by 1 with each od
def max_od_id():
	query = """SELECT MAX(od_id)
	FROM order_delivery"""

	conn=connect('restaurant')
	cursor=conn.cursor(buffered=True)
	cursor.execute(query)
	for result in cursor.fetchall():
		max_od = result[0]

	cursor.close()
	disconnect(conn)

	if max_od==None:
		return 0

	return max_od

#broadcast od_id to delivers near the restaurant
#here the location of the restaurant is determined by restaurant_area() 
def publish_od(od_id, re_add):
	connection=pika.BlockingConnection(pika.ConnectionParameters
		(host='localhost'))
	channel=connection.channel()

	channel.exchange_declare(exchange='request',
		exchange_type='direct')

	message=str(od_id)
	routing_key=restaurant_area(re_add)
	channel.basic_publish(exchange='request',
		routing_key=routing_key,
		body=message)
	print(' [x] Requested delivery for order id: %r around area %r' % (message, routing_key))
	connection.close()

"""
  a qsuedo-method that return the area that the restaurant is in
  here this method is hardcoded to return 1 for illustrative purposes
  it is supposed to be replaced by an API dealing with locations
"""
def restaurant_area(re_add):
	return '1'

"""
the only method restaurant service needs to directly call
update order state, create new order_delivery row, and broadcast od information to all nearby delivers
"""
def order_ready_to_be_delivered(order_id):
	update_order_state(order_id, 3)

	re_id=retrieve_re_id(order_id)
	re_add=retrieve_re_add(re_id)
	add=retrieve_add(order_id)
	print('order number %s from restaurant %s is ready to be delivered' % (order_id, re_id))
	od_id=create_od(order_id, re_add, add)

	publish_od(od_id, re_add)

order_id=2
order_ready_to_be_delivered(2)