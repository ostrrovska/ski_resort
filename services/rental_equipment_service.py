from models.rental_equipment import RentalEquipment
from models import db
from services.equipment_service import EquipmentService
from services.rental_service import RentalService

class RentalEquipmentService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_by=None, filter_value=None):
        query = RentalEquipment.query

        if filter_by and filter_value is not None:
            if filter_by in ['rental_id', 'equipment_id']:
                query = query.filter(getattr(RentalEquipment, filter_by) == filter_value)

        if sort_by in ['rental_id', 'equipment_id']:
            sort_column = getattr(RentalEquipment, sort_by)
            if sort_order == 'desc':
                sort_column = sort_column.desc()
            query = query.order_by(sort_column)

        return query.all()

    @staticmethod
    def get_by_id(rental_id, equipment_id):
        return db.session.get(RentalEquipment, (rental_id, equipment_id))

    @staticmethod
    def add(rental_id, equipment_id):
        if not RentalService.get_by_id(rental_id):
            raise ValueError(f"Rental with id={rental_id} is not found.")
        if not EquipmentService.get_by_id(equipment_id):
            raise ValueError(f"Equipment with id={equipment_id} is not found.")

        new_entry = RentalEquipment(rental_id=rental_id, equipment_id=equipment_id)
        db.session.add(new_entry)
        db.session.commit()
        return new_entry

    @staticmethod
    def update(old_rental_id, old_equipment_id, new_rental_id, new_equipment_id):

        if not RentalService.get_by_id(new_rental_id):
            raise ValueError(f"Rental with id={new_rental_id} is not found.")
        if not EquipmentService.get_by_id(new_equipment_id):
            raise ValueError(f"Equipment with id={new_equipment_id} is not found.")

        entry = RentalEquipmentService.get_by_id(old_rental_id, old_equipment_id)
        if not entry:
            return None

        db.session.delete(entry)
        db.session.commit()

        updated_entry = RentalEquipment(rental_id=new_rental_id, equipment_id=new_equipment_id)
        db.session.add(updated_entry)
        db.session.commit()

        return updated_entry

    @staticmethod
    def delete(rental_id, equipment_id):
        entry = RentalEquipmentService.get_by_id(rental_id, equipment_id)
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return True
        return False