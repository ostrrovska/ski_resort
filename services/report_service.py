from models import db
from models.client import Client
from models.employee import Employee
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
from models.schedule import Schedule
from models.tariff import Tariff


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

    def get_clients_with_exhausted_passes(self):
        """Part of Query 6: Get clients with passes that have 0 or fewer remaining lifts."""
        query = db.session.query(
            Client.id.label('client_id'),
            Client.full_name,
            Client.email,
            Pass.id.label('pass_id'),
            PassType.name.label('pass_type_name'),
            Pass.remaining_lifts
        ).join(Pass, Client.id == Pass.client_id) \
            .join(PassType, Pass.pass_type_id == PassType.id) \
            .join(Key, Client.authorization_fkey == Key.id) \
            .filter(Key.is_approved == True) \
            .filter(Pass.remaining_lifts <= 0) \
            .order_by(Client.full_name, Pass.id)

        return query.all()

    def get_clients_with_over_15_lifts_daily(self, specific_date):
        """Part of Query 6: Get clients who used lifts more than 15 times on a specific day."""
        if not specific_date:
            return []

        query = db.session.query(
            Client.id.label('client_id'),
            Client.full_name,
            Client.email,
            func.count(LiftUsage.id).label('lift_count')
        ).join(LiftUsage, Client.id == LiftUsage.client_id) \
            .join(Key, Client.authorization_fkey == Key.id) \
            .filter(Key.is_approved == True) \
            .filter(LiftUsage.usage_date == specific_date) \
            .group_by(Client.id, Client.full_name, Client.email) \
            .having(func.count(LiftUsage.id) > 15) \
            .order_by(desc('lift_count'), Client.full_name)

        return query.all()

    def get_clients_bought_pass_by_month(self, pass_name, year, month):
        """Part of Query 7: Get clients who bought a specific pass type in a specific month and year."""
        if not year or not month or not pass_name:
            return []

        query = db.session.query(
            Client.id.label('client_id'),
            Client.full_name,
            Client.email,
            Pass.id.label('pass_id'),
            Pass.purchase_date
        ).join(Pass, Client.id == Pass.client_id) \
            .join(PassType, Pass.pass_type_id == PassType.id) \
            .join(Key, Client.authorization_fkey == Key.id) \
            .filter(Key.is_approved == True) \
            .filter(PassType.name.ilike(pass_name)) \
            .filter(extract('year', Pass.purchase_date) == year) \
            .filter(extract('month', Pass.purchase_date) == month) \
            .order_by(Client.full_name, Pass.purchase_date)

        return query.all()

    def get_equipment_tariffs_with_weekday_discount(self):
        """
        Part of Query 8: Get tariff information for all equipment types,
        including base prices and weekday discounts.
        """
        query = db.session.query(
            EquipmentType.name.label('equipment_type_name'),
            EquipmentType.description,
            Tariff.price_per_hour.label('base_price_hour'),
            Tariff.price_per_day.label('base_price_day'),
            Tariff.weekday_discount
        ).join(Tariff, EquipmentType.id == Tariff.equipment_type_id) \
            .order_by(EquipmentType.name)

        return query.all()

    # --- Query 9: Client Visit Statistics ---

    def get_clients_visited_in_date_range(self, start_date, end_date):
        """Part of Query 9: Get clients who used a lift (visited) in a specific date range."""
        if not start_date or not end_date:
            return []

        query = db.session.query(
            Client
        ).join(LiftUsage, Client.id == LiftUsage.client_id) \
            .join(Key, Client.authorization_fkey == Key.id) \
            .filter(Key.is_approved == True) \
            .filter(LiftUsage.usage_date.between(start_date, end_date)) \
            .distinct(Client.id) \
            .order_by(Client.id, Client.full_name)

        return query.all()

    def get_clients_visited_more_than_x_times(self, visit_count_threshold):
        """Part of Query 9: Get clients who visited (on distinct days) more than X times."""
        if not visit_count_threshold:
            return []

        # Subquery to count distinct visit days per client
        visit_counts_sq = db.session.query(
            LiftUsage.client_id,
            func.count(func.distinct(LiftUsage.usage_date)).label('visit_count')
        ).group_by(LiftUsage.client_id).subquery()

        # Main query
        query = db.session.query(
            Client,
            visit_counts_sq.c.visit_count
        ).join(visit_counts_sq, Client.id == visit_counts_sq.c.client_id) \
            .join(Key, Client.authorization_fkey == Key.id) \
            .filter(Key.is_approved == True) \
            .filter(visit_counts_sq.c.visit_count > visit_count_threshold) \
            .order_by(desc('visit_count'), Client.full_name)

        return query.all()

    # --- Query 10: Employee Work Statistics ---

    def get_employee_rental_details(self):
        """Part of Query 10: Get all employees and the equipment they have issued."""

        query = db.session.query(
            Employee.full_name,
            Employee.position,
            Rental.id.label('rental_id'),
            Rental.rental_date,
            Equipment.model,
            EquipmentType.name.label('equipment_type')
        ).join(Rental, Employee.id == Rental.employee_id) \
            .join(RentalEquipment, Rental.id == RentalEquipment.rental_id) \
            .join(Equipment, RentalEquipment.equipment_id == Equipment.id) \
            .join(EquipmentType, Equipment.type_id == EquipmentType.id) \
            .order_by(Employee.full_name, Rental.rental_date)

        return query.all()

    def get_employees_working_on_date(self, specific_date):
        """Part of Query 10: Get employees who were scheduled to work on a specific date."""
        if not specific_date:
            return []

        query = db.session.query(
            Employee,
            Schedule.shift_start,
            Schedule.shift_end
        ).join(Schedule, Employee.id == Schedule.employee_id) \
            .filter(Schedule.work_date == specific_date) \
            .order_by(Employee.full_name)

        return query.all()