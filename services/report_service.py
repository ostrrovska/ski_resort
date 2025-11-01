from models import db
from models.client import Client
from models.equipment import Equipment
from models.equipment_type import EquipmentType
from models.passes import Pass
from models.pass_type import PassType
from sqlalchemy import desc, func  # Для сортування

from models.rental import Rental
from models.rental_equipment import RentalEquipment


class ReportService:

    def get_clients_and_passes(self):
        """Запит 1: Отримати клієнтів та їхні придбані абонементи."""
        query = db.session.query(
            Client.id.label('client_id'),
            Client.full_name,
            Client.email,
            Pass.id.label('pass_id'),
            PassType.name.label('pass_type_name'),
            Pass.purchase_date,
            Pass.valid_from,
            Pass.valid_to,
            Pass.remaining_lifts,
            Pass.remaining_hours
        ).join(Pass, Client.id == Pass.client_id) \
         .join(PassType, Pass.pass_type_id == PassType.id) \
         .order_by(Client.full_name, Pass.purchase_date)


        return query.all()

# --- NEW METHODS FOR QUERY 2 ---
    def get_most_rented_equipment_weekly(self, start_date, end_date):
        """Part of Query 2: Get equipment rented most often in the specified period (week)."""
        if not start_date or not end_date:
            return []
        query = db.session.query(
            Equipment.id,
            Equipment.model,
            EquipmentType.name.label('type_name'),
            func.count(RentalEquipment.equipment_id).label('rental_count')
        ).join(RentalEquipment, Equipment.id == RentalEquipment.equipment_id) \
         .join(Rental, RentalEquipment.rental_id == Rental.id) \
         .join(EquipmentType, Equipment.type_id == EquipmentType.id) \
         .filter(Rental.rental_date >= start_date, Rental.rental_date <= end_date) \
         .group_by(Equipment.id, Equipment.model, EquipmentType.name) \
         .order_by(desc('rental_count')) # Order by most rented
        return query.all() # Return all results sorted by count

    def get_equipment_count_by_type_daily(self, date_):
        """Part of Query 2: Get count of rented equipment by type for a specific day."""
        if not date_:
            return []
        query = db.session.query(
            EquipmentType.name.label('type_name'),
            func.count(RentalEquipment.equipment_id).label('rental_count')
        ).select_from(Rental) \
         .join(RentalEquipment, Rental.id == RentalEquipment.rental_id) \
         .join(Equipment, RentalEquipment.equipment_id == Equipment.id) \
         .join(EquipmentType, Equipment.type_id == EquipmentType.id) \
         .filter(Rental.rental_date == date_) \
         .group_by(EquipmentType.name) \
         .order_by(EquipmentType.name)
        return query.all()
    # --- END NEW METHODS ---