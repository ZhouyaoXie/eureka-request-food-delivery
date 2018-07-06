# request-food-delivery
*restaurant.py* publishes order delivery requests to specified food couriers;
*deliver.py* receives order delivery requests.
Both directly manipulates the database to keep data updated.

### Software Setup
- MySQL v8.0
- RabbitMQ Server

### Database Setup
In MySQL command line enter:
```
create database db;
use db; 
```
Then run db_users.txt, sql_tables.txt, sample_data.txt respectively using source command.

### Run request-food-delivery
Open two command prompt windows. Run deliver.py in one window.
The prompt should look like this:
```
Waiting for order delivery request... To exit press CTRL+C
```
Run restaurant.py in another window and see the following prompt in the first window:
```
Successfully requested to deliver order, order delivery id:2
```

### Functionality Details
##### restaurant.py
While users (restaurant servers) only need to access `order_ready_to_be_delivered()` method, restaurant.py also provides methods that allow restaurant service to:
- directly manipulates the database
    + update_order_state()
    + create_od()
- retrieve relevant data from the database, including:
    + retrieve_re_id()
    + retrieve_re_add()
    + retrieve_add()
    + max_od_id()
- publish an order delivery request via message queue to specified food couriers
    + publish_od()

##### deliver.py
Similarly, deliver.py also provides other functionality besides the two methods users (food couriers) have access to(that is, receive_order() and request_to_deliver_order()):
- updata database
    + update_de_id()
    + update_od_state()
    + update_order_state()
- retrieve data
    + retrieve_od_state()
    + retrieve_order_id()
