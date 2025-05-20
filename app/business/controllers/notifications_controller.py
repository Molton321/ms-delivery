from flask_socketio import emit
from app import socketio
from datetime import datetime

class NotificationController:
    @staticmethod
    def notify(title, message, extra_data=None):
        """Emite una notificación global a todos los clientes conectados"""
        data = {
            "title": title,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "extra": extra_data or {}
        }
        socketio.emit("notificacion", data)
        print(f"📨 Notificación global enviada: {data}")
