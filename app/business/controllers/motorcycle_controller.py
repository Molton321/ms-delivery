from app import db,socketio
from app.business.models.motorcycle import Motorcycle
from flask import jsonify
import json
import eventlet

# Carga las coordenadas una vez
with open("coordinates/routes/example_1.json", "r") as f:
    coordenadas = json.load(f)

# Control de tareas activas por placa
tareas_activas = {}

class MotorcycleController:
    @staticmethod
    def get_all():
        motorcycles = Motorcycle.query.all()
        return [motorcycle.to_dict() for motorcycle in motorcycles]
    
    @staticmethod
    def get_by_id(motorcycle_id):
        motorcycle = Motorcycle.query.get_or_404(motorcycle_id)
        return motorcycle.to_dict()
    
    @staticmethod
    def create(data):
        new_motorcycle = Motorcycle(
            license_plate=data.get('license_plate'),
            brand=data.get('brand'),
            year=data.get('year'),
            status=data.get('status', 'available')
        )
        
        db.session.add(new_motorcycle)
        db.session.commit()
        
        return new_motorcycle.to_dict(), 201
    
    @staticmethod
    def update(motorcycle_id, data):
        motorcycle = Motorcycle.query.get_or_404(motorcycle_id)
        
        if 'license_plate' in data:
            motorcycle.license_plate = data['license_plate']
        if 'brand' in data:
            motorcycle.brand = data['brand']
        if 'year' in data:
            motorcycle.year = data['year']
        if 'status' in data:
            motorcycle.status = data['status']
        
        db.session.commit()
        
        return motorcycle.to_dict()
    
    @staticmethod
    def delete(motorcycle_id):
        motorcycle = Motorcycle.query.get_or_404(motorcycle_id)
        
        db.session.delete(motorcycle)
        db.session.commit()
        
        return {"message": "Motorcycle deleted successfully"}, 200



    @staticmethod
    def start_tracking_by_plate(plate):
        motorcycle = Motorcycle.query.filter_by(license_plate=plate).first()
        if not motorcycle:
            return {"status": "error", "message": "Motocicleta no encontrada"}, 404

        if plate in tareas_activas:
            return {"status": "ok", "message": f"Transmisión ya activa para {plate}"}

        # Inicia la transmisión de coordenadas en segundo plano
        socketio.start_background_task(MotorcycleController._emit_coordinates, plate)
        tareas_activas[plate] = True
        return {"status": "ok", "message": f"Transmisión iniciada para {plate}"}

    @staticmethod
    def _emit_coordinates(plate):
        i = 0
        total = len(coordenadas)
        while tareas_activas.get(plate, False):
            coord = coordenadas[i]
            socketio.emit(plate, coord)
            print(f"[{plate}] Emitiendo coordenada {i}: {coord}")
            i = (i + 1) % total
            eventlet.sleep(5)

    @staticmethod
    def stop_tracking_by_plate(plate):
        if plate in tareas_activas:
            tareas_activas[plate] = False
            tareas_activas.pop(plate, None)  # Limpieza
            return {"status": "ok", "message": f"Transmisión detenida para {plate}"}
        else:
            return {"status": "error", "message": f"No hay transmisión activa para {plate}"}, 404