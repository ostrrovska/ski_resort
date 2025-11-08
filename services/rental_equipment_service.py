from models.rental_equipment import RentalEquipment
from models import db
from services.equipment_service import EquipmentService
from services.rental_service import RentalService
from utils.query_helper import QueryHelper


class RentalEquipmentService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_cols=None, filter_ops=None, filter_vals=None):
        return QueryHelper.get_all(
            RentalEquipment,
            sort_by,
            sort_order,
            filter_cols,
            filter_ops,
            filter_vals
        )

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