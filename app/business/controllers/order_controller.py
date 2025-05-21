from app import db
from app.business.models.order import Order
from app.business.models.menu import Menu
from app.business.models.product import Product
from app.business.models.customer import Customer
from flask import jsonify
from app import socketio

class OrderController:
    @staticmethod
    def get_all():
        orders = Order.query.all()
        return [order.to_dict() for order in orders]
    
    @staticmethod
    def get_by_id(order_id):
        order = Order.query.get_or_404(order_id)
        return order.to_dict()
    
    @staticmethod
    def create(data):
    # Obtener información del menú
        menu_item = Menu.query.get_or_404(data.get('menu_id'))
        quantity = data.get('quantity', 1)
        total_price = menu_item.price * quantity

        # Crear la orden
        new_order = Order(
            customer_id=data.get('customer_id'),
            menu_id=data.get('menu_id'),
            motorcycle_id=data.get('motorcycle_id'),
            quantity=quantity,
            total_price=total_price,
            status=data.get('status', 'pending')
        )

        db.session.add(new_order)
        db.session.commit()

        # 🔍 Obtener información adicional para la notificación
        product = Product.query.get(menu_item.product_id)
        customer = Customer.query.get(data.get('customer_id'))

        # 📨 Enviar notificación
        socketio.emit("notificacion", {
            "title": "🎉 ¡Hay un nuevo pedido!",
            "message": f"🧾 {customer.name} ordenó el producto {product.name}."
        })


        
        
        return new_order.to_dict(), 201
    
    @staticmethod
    def update(order_id, data):
        order = Order.query.get_or_404(order_id)
        
        if 'customer_id' in data:
            order.customer_id = data['customer_id']
        if 'menu_id' in data:
            order.menu_id = data['menu_id']
            # Recalculate total price if menu or quantity changes
            menu_item = Menu.query.get_or_404(data['menu_id'])
            order.total_price = menu_item.price * order.quantity
        if 'motorcycle_id' in data:
            order.motorcycle_id = data['motorcycle_id']
        if 'quantity' in data:
            order.quantity = data['quantity']
            # Recalculate total price
            menu_item = Menu.query.get_or_404(order.menu_id)
            order.total_price = menu_item.price * data['quantity']
        if 'status' in data:
            order.status = data['status']
        
        db.session.commit()
        
        return order.to_dict()
    
    @staticmethod
    def delete(order_id):
        order = Order.query.get_or_404(order_id)
        
        db.session.delete(order)
        db.session.commit()
        
        return {"message": "Order deleted successfully"}, 200