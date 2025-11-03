from models import db
from models.client import Client
from models.equipment import Equipment
from models.equipment_type import EquipmentType
from models.key import Key
from models.lift import Lift
from models.lift_usage import LiftUsage
from models.passes import Pass
from models.pass_type import PassType
from sqlalchemy import desc, func, extract  # Для сортування

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
         .join(Key, Client.authorization_fkey == Key.id) \
         .filter(Key.is_approved == True) \
         .order_by(Client.full_name, Pass.purchase_date)


        return query.all()

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
         .order_by(desc('rental_count'), Equipment.model.asc()) # Order by most rented
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

#Query 3: Get the count of passes sold per day in a period. Get the count of passes sold by type in a period.

    def get_pass_sales_by_day(self, start_date, end_date):
        """Part of Query 3: Get the count of passes sold per day in a period."""
        if not start_date or not end_date:
            return []

        query = db.session.query(
            Pass.purchase_date,
            func.count(Pass.id).label('sales_count')
        ).filter(
            Pass.purchase_date >= start_date,
            Pass.purchase_date <= end_date
        ).group_by(
            Pass.purchase_date
        ).order_by(
            Pass.purchase_date.asc()
        )
        return query.all()

    def get_pass_sales_by_type(self, start_date, end_date):
        """Part of Query 3: Get the count of passes sold by type in a period."""
        if not start_date or not end_date:
            return []

        query = db.session.query(
            PassType.name.label('pass_type_name'),
            func.count(Pass.id).label('sales_count')
        ).join(
            PassType, Pass.pass_type_id == PassType.id
        ).filter(
            Pass.purchase_date >= start_date,
            Pass.purchase_date <= end_date
        ).group_by(
            PassType.name
        ).order_by(
            PassType.name.asc()
        )
        return query.all()
#query 4: Get most used lifts in the specified period.

    def get_most_used_lifts_by_period(self, start_date, end_date):
        """Part of Query 4: Get most used lifts in the specified period."""
        if not start_date or not end_date:
            return []

        query = db.session.query(
            Lift.name.label('lift_name'),
            func.count(LiftUsage.id).label('usage_count')
        ).join(
            Lift, LiftUsage.lift_id == Lift.id
        ).filter(
            LiftUsage.usage_date >= start_date,
            LiftUsage.usage_date <= end_date
        ).group_by(
            Lift.id, Lift.name
        ).order_by(
            desc('usage_count')
        )
        return query.all()

# --- Query 5: Get total rental revenue grouped by year and month. ---

    def get_rental_revenue_by_month(self, start_date, end_date):
        """Part of Query 5: Get total rental revenue grouped by year and month."""
        if not start_date or not end_date:
            return []

        query = db.session.query(
            extract('year', Rental.rental_date).label('year'),
            extract('month', Rental.rental_date).label('month'),
            func.sum(Rental.total_price).label('total_revenue')
        ).filter(
            Rental.rental_date.between(start_date, end_date)
        ).group_by(
            extract('year', Rental.rental_date),
            extract('month', Rental.rental_date)
        ).order_by(
            extract('year', Rental.rental_date).asc(),
            extract('month', Rental.rental_date).asc()
        )
        return query.all()

    def get_rental_revenue_by_quarter(self, start_date, end_date):
        """Part of Query 5: Get total rental revenue grouped by year and quarter."""
        if not start_date or not end_date:
            return []

        query = db.session.query(
            extract('year', Rental.rental_date).label('year'),
            extract('quarter', Rental.rental_date).label('quarter'),
            func.sum(Rental.total_price).label('total_revenue')
        ).filter(
            Rental.rental_date.between(start_date, end_date)
        ).group_by(
            extract('year', Rental.rental_date),
            extract('quarter', Rental.rental_date)
        ).order_by(
            extract('year', Rental.rental_date).asc(),
            extract('quarter', Rental.rental_date).asc()
        )
        return query.all()
