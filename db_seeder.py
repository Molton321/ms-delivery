import os
import sys
import random
from datetime import datetime, timedelta
from faker import Faker
from app import db, create_app
from app.business.models.customer import Customer
from app.business.models.driver import Driver
from app.business.models.motorcycle import Motorcycle
from app.business.models.restaurant import Restaurant
from app.business.models.product import Product
from app.business.models.menu import Menu
from app.business.models.order import Order
from app.business.models.address import Address
from app.business.models.shift import Shift
from app.business.models.issue import Issue
from app.business.models.photo import Photo

# Initialize the application
app = create_app()
app.app_context().push()

# Initialize Faker
fake = Faker()

# Constants for status fields
ORDER_STATUSES = ['pending', 'in_progress', 'delivered', 'cancelled']
DRIVER_STATUSES = ['available', 'on_shift', 'unavailable']
MOTORCYCLE_STATUSES = ['available', 'in_use', 'maintenance']
ISSUE_TYPES = ['accident', 'breakdown', 'maintenance']
ISSUE_STATUSES = ['open', 'in_progress', 'resolved']
SHIFT_STATUSES = ['active', 'completed', 'cancelled']

# Helper functions
def random_date(start_date, end_date):
    """Generate a random date between start_date and end_date"""
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)

def seed_restaurants():
    """Seed the restaurants table with at least 30 records"""
    print("Seeding restaurants...")
    restaurants = []
    
    for i in range(1, 31):
        restaurant = Restaurant(
            name=fake.company() + ' ' + random.choice(['Restaurant', 'Café', 'Grill', 'Bistro', 'Eatery']),
            address=fake.address(),
            phone=fake.phone_number(),
            email=fake.company_email(),
            created_at=random_date(datetime.now() - timedelta(days=365), datetime.now())
        )
        restaurants.append(restaurant)
    
    db.session.add_all(restaurants)
    db.session.commit()
    
    return restaurants

def seed_products():
    """Seed the products table with at least 30 records"""
    print("Seeding products...")
    products = []
    
    categories = ['Main Course', 'Appetizer', 'Dessert', 'Beverage', 'Side Dish']
    
    for i in range(1, 31):
        product = Product(
            name=fake.word().capitalize() + ' ' + random.choice(['Burger', 'Pizza', 'Salad', 'Sandwich', 'Pasta', 'Steak', 'Fish']),
            description=fake.sentence(),
            price=round(random.uniform(5.0, 50.0), 2),
            category=random.choice(categories),
            created_at=random_date(datetime.now() - timedelta(days=365), datetime.now())
        )
        products.append(product)
    
    db.session.add_all(products)
    db.session.commit()
    
    return products

def seed_menus(restaurants, products):
    """Seed the menus table linking restaurants and products"""
    print("Seeding menus...")
    menus = []
    
    # Each restaurant will have multiple menu items
    for restaurant in restaurants:
        # Select random products for this restaurant
        num_products = random.randint(5, 10)
        restaurant_products = random.sample(products, num_products)
        
        for product in restaurant_products:
            # Menu price might be different from product price
            menu = Menu(
                restaurant_id=restaurant.id,
                product_id=product.id,
                price=round(product.price * random.uniform(0.9, 1.2), 2),  # Add some variation to prices
                availability=random.choice([True, True, True, False]),  # 75% chance of being available
                created_at=random_date(datetime.now() - timedelta(days=365), datetime.now())
            )
            menus.append(menu)
    
    db.session.add_all(menus)
    db.session.commit()
    
    return menus

def seed_customers():
    """Seed the customers table with at least 30 records"""
    print("Seeding customers...")
    customers = []
    
    for i in range(1, 31):
        customer = Customer(
            name=fake.name(),
            email=fake.email(),
            phone=fake.phone_number(),
            created_at=random_date(datetime.now() - timedelta(days=365), datetime.now())
        )
        customers.append(customer)
    
    db.session.add_all(customers)
    db.session.commit()
    
    return customers

def seed_drivers():
    """Seed the drivers table with at least 30 records"""
    print("Seeding drivers...")
    drivers = []
    
    for i in range(1, 31):
        driver = Driver(
            name=fake.name(),
            license_number=f"DL{fake.random_number(8)}",
            phone=fake.phone_number(),
            email=fake.email(),
            status=random.choice(DRIVER_STATUSES),
            created_at=random_date(datetime.now() - timedelta(days=365), datetime.now())
        )
        drivers.append(driver)
    
    db.session.add_all(drivers)
    db.session.commit()
    
    return drivers

def seed_motorcycles():
    """Seed the motorcycles table with at least 30 records"""
    print("Seeding motorcycles...")
    motorcycles = []
    
    brands = ['Honda', 'Yamaha', 'Suzuki', 'Kawasaki', 'Ducati', 'Harley-Davidson', 'BMW', 'KTM']
    
    for i in range(1, 31):
        motorcycle = Motorcycle(
            license_plate=f"{fake.random_letter()}{fake.random_letter()}{fake.random_letter()}-{fake.random_number(4)}",
            brand=random.choice(brands),
            year=random.randint(2015, 2025),
            status=random.choice(MOTORCYCLE_STATUSES),
            created_at=random_date(datetime.now() - timedelta(days=365), datetime.now())
        )
        motorcycles.append(motorcycle)
    
    db.session.add_all(motorcycles)
    db.session.commit()
    
    return motorcycles

def seed_issues(motorcycles):
    """Seed the issues table with at least 30 records"""
    print("Seeding issues...")
    issues = []
    
    # Some motorcycles will have multiple issues, some may have none
    motorcycles_with_issues = random.sample(motorcycles, min(len(motorcycles), 20))
    
    for motorcycle in motorcycles_with_issues:
        num_issues = random.randint(1, 3)
        
        for _ in range(num_issues):
            issue_date = random_date(datetime.now() - timedelta(days=180), datetime.now())
            
            issue = Issue(
                motorcycle_id=motorcycle.id,
                description=fake.paragraph(),
                issue_type=random.choice(ISSUE_TYPES),
                date_reported=issue_date,
                status=random.choice(ISSUE_STATUSES),
                created_at=issue_date
            )
            issues.append(issue)
    
    db.session.add_all(issues)
    db.session.commit()
    
    return issues

def seed_orders(customers, menus, motorcycles):
    """Seed the orders table with at least 30 records"""
    print("Seeding orders...")
    orders = []
    
    # Ensure we have at least 30 orders
    for i in range(1, 31):
        customer = random.choice(customers)
        menu = random.choice(menus)
        quantity = random.randint(1, 5)
        total_price = round(menu.price * quantity, 2)
        
        # 70% of orders have a motorcycle assigned
        motorcycle_id = random.choice(motorcycles).id if random.random() < 0.7 else None
        
        order_date = random_date(datetime.now() - timedelta(days=90), datetime.now())
        
        order = Order(
            customer_id=customer.id,
            menu_id=menu.id,
            motorcycle_id=motorcycle_id,
            quantity=quantity,
            total_price=total_price,
            status=random.choice(ORDER_STATUSES),
            created_at=order_date
        )
        
        db.session.add(order)
        db.session.flush()  # Generate an ID without committing
        
        # Create address for the order
        address = Address(
            order_id=order.id,
            street=fake.street_address(),
            city=fake.city(),
            state=fake.state(),
            postal_code=fake.zipcode(),
            additional_info=fake.sentence() if random.random() < 0.3 else None,
            created_at=order_date
        )
        
        db.session.add(address)
        orders.append(order)
    
    db.session.commit()
    
    return orders

def seed_shifts(drivers, motorcycles):
    """Seed the shifts table with at least 30 records"""
    print("Seeding shifts...")
    shifts = []
    
    for i in range(1, 31):
        driver = random.choice(drivers)
        motorcycle = random.choice(motorcycles)
        
        start_time = random_date(datetime.now() - timedelta(days=30), datetime.now())
        status = random.choice(SHIFT_STATUSES)
        
        # If shift is completed, it has an end time
        end_time = None
        if status == 'completed':
            end_time = start_time + timedelta(hours=random.randint(4, 8))
        
        shift = Shift(
            driver_id=driver.id,
            motorcycle_id=motorcycle.id,
            start_time=start_time,
            end_time=end_time,
            status=status,
            created_at=start_time
        )
        shifts.append(shift)
    
    db.session.add_all(shifts)
    db.session.commit()
    
    return shifts

def main():
    """Main function to orchestrate the database seeding"""
    try:
        print("Starting database seeding...")
        
        # First: Check if the database already has data
        customer_count = db.session.query(Customer).count()
        if customer_count > 0:
            confirmation = input("Database already contains data. Do you want to clear existing data and reseed? (y/N): ")
            if confirmation.lower() != 'y':
                print("Seeding canceled.")
                return
            
            # Clear all tables
            db.session.query(Address).delete()
            db.session.query(Order).delete()
            db.session.query(Shift).delete()
            db.session.query(Photo).delete()
            db.session.query(Issue).delete()
            db.session.query(Menu).delete()
            db.session.query(Product).delete()
            db.session.query(Restaurant).delete()
            db.session.query(Motorcycle).delete()
            db.session.query(Driver).delete()
            db.session.query(Customer).delete()
            db.session.commit()
        
        # Seed tables in the correct order to respect foreign key constraints
        restaurants = seed_restaurants()
        products = seed_products()
        menus = seed_menus(restaurants, products)
        customers = seed_customers()
        drivers = seed_drivers()
        motorcycles = seed_motorcycles()
        issues = seed_issues(motorcycles)
        orders = seed_orders(customers, menus, motorcycles)
        shifts = seed_shifts(drivers, motorcycles)
        
        print("Database seeding completed successfully!")
        print(f"Created: {len(restaurants)} restaurants, {len(products)} products, {len(menus)} menu items")
        print(f"Created: {len(customers)} customers, {len(drivers)} drivers, {len(motorcycles)} motorcycles")
        print(f"Created: {len(issues)} issues, {len(orders)} orders, {len(shifts)} shifts")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding database: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

