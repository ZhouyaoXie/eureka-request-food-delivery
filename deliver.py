import threading
import pika
import sys
import mysql.connector
from mysql.connector import Error, MySQLConnection
from database import connect, disconnect

"""
wait for od_id from nearby restaurant
if one is received, send od_id to be processed by request_to_deliver_order()
"""
def receive_order(de_id):
	od_id=-1

	connection=pika.BlockingConnection(pika.ConnectionParameters
		(host='localhost'))
	channel=connection.channel()

	channel.exchange_declare(exchange='request',
		exchange_type='direct')

	result=channel.queue_declare(exclusive=True)
	queue_name=result.method.queue
	binding_key=get_location(de_id)

	channel.queue_bind(exchange='request',
		queue=queue_name,
		routing_key=binding_key)

	print('Waiting for order delivery request... To exit press CTRL+C')

	def callback(ch, method, properties, body):
		#channel.close()
		od_id=int(body.decode())
		print(od_id)

		try:
		   t1 = threading.Thread(target=request_to_deliver_order,args=(od_id, de_id,))
		   t1.start()
		except:
		   print('Error: unable to start thread')

	channel.basic_consume(callback,
		queue=queue_name,
		no_ack=True)

	channel.start_consuming()

def get_location(de_id):
	return '1'

def update_de_id(od_id, de_id):
	query="""UPDATE order_delivery
	SET de_id = %s
	WHERE od_id= %s"""

	data=(de_id, od_id)

	conn=connect('deliver')
	cursor=conn.cursor()
	cursor.execute(query, data)
	conn.commit()
	print('updated delivery id %s for od %s' % (de_id, od_id))

	disconnect(conn)

def retrieve_od_state(od_id):
	query="""SELECT od_state
	FROM order_delivery
	WHERE od_id=%s""" % od_id
	od_state=-1

	conn=connect('deliver')

	cursor=conn.cursor()
	cursor.execute(query)
	for result in cursor.fetchall():
		od_state=result[0]
		print('od %s is in state %s' % (od_id, od_state))

	conn.commit()
	disconnect(conn)

	return od_state

def update_od_state(od_id, od_state):
	query="""UPDATE order_delivery
	SET od_state = %s
	WHERE od_id= %s"""

	data=(od_state, od_id)

	conn=connect('deliver')

	cursor=conn.cursor()
	cursor.execute(query, data)
	conn.commit()
	print('update od %s to state %s' % (od_id, od_state))

	disconnect(conn)

def retrieve_order_id(od_id):
	order_id=None
	query="""SELECT order_id
	FROM order_delivery
	WHERE od_id=%s""" % od_id

	conn=connect('deliver')
	cursor=conn.cursor()
	cursor.execute(query)
	for result in cursor.fetchall():
		order_id=result[0]

	conn.commit()

	disconnect(conn)

def update_order_state(order_id, order_state):
	query="""UPDATE mel_order
	SET order_state = %s
	WHERE order_id= %s"""

	data=(order_state, order_id)

	conn=connect('deliver')

	cursor=conn.cursor()
	cursor.execute(query, data)
	conn.commit()
	print('update order %s to state %s' % (order_id, order_state))

	disconnect(conn)

"""
deliver service requests to deliver a specific order by retrieving its od_state
if od_state is 1, it is waiting to be delivered
	deliver service will mark this od with de_id
if od_state is 0, 2, or 3, this order can no longer be delivered
	deliver service will wait for another od sent by nearby restaurant
"""
def request_to_deliver_order(od_id, de_id):
	update_de_id(od_id, de_id)
	if retrieve_od_state(od_id)==1:
		update_od_state(od_id, 2)
	else:
		print('Something went wrong... Please try another order.')
		return False
	order_id=retrieve_order_id(od_id)
	update_order_state(order_id, 4)
	print('Successfully requested to deliver order, order delivery id:', od_id)

def confirm_order_delivered(od_id):
	update_od_state(od_id, 3)
	update_order_state(retrieve_order_id(od_id), 6)

de_id=1
od_id=receive_order(de_id)
request_to_deliver_order(od_id, de_id)