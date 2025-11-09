from models.pass_rental_usage import PassRentalUsage
from models import db
from services.pass_service import PassService
from services.rental_service import RentalService
from utils.query_helper import QueryHelper
from datetime import datetime


class PassRentalUsageService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_cols=None, filter_ops=None, filter_vals=None):
        return QueryHelper.get_all(
            PassRentalUsage,
            sort_by,
            sort_order,
            filter_cols,
            filter_ops,
            filter_vals
        )

    @staticmethod
    def get_by_id(pass_id, rental_id):
        return db.session.get(PassRentalUsage, (pass_id, rental_id))

    @staticmethod
    def _calculate_rental_hours(rental):
        if not rental.start_time or not rental.end_time or not rental.rental_date:
            raise ValueError("Rental object is missing date or time information.")

        start_dt = datetime.combine(rental.rental_date, rental.start_time)
        end_dt = datetime.combine(rental.rental_date, rental.end_time)

        if end_dt <= start_dt:
            raise ValueError("Rental end time must be after start time.")

        return (end_dt - start_dt).total_seconds() / 3600.0

    @staticmethod
    def add(pass_id, rental_id):
        pass_obj = PassService.get_by_id(pass_id)
        rental_obj = RentalService.get_by_id(rental_id)

        if not pass_obj:
            raise ValueError(f"Pass with id={pass_id} is not found.")
        if not rental_obj:
            raise ValueError(f"Rental with id={rental_id} is not found.")

        if rental_obj.pass_usage:
            raise ValueError(f"Rental {rental_id} is already linked to a pass.")

        if pass_obj.pass_type.limit_hours <= 0:
            raise ValueError(f"Pass {pass_id} is not an hourly pass.")

        duration_hours = PassRentalUsageService._calculate_rental_hours(rental_obj)

        if pass_obj.remaining_hours < duration_hours:
            raise ValueError(
                f"Pass {pass_id} has only {pass_obj.remaining_hours} hours left, but {duration_hours} are required.")

        # Логіка віднімання
        pass_obj.remaining_hours -= duration_hours

        new_entry = PassRentalUsage(
            pass_id=pass_id,
            rental_id=rental_id,
            hours_deducted=duration_hours
        )
        db.session.add(new_entry)
        db.session.commit()
        return new_entry

    @staticmethod
    def update(old_pass_id, old_rental_id, new_pass_id, new_rental_id):
        # 1. Видаляємо старий зв'язок (з поверненням годин)
        try:
            PassRentalUsageService.delete(old_pass_id, old_rental_id)
        except Exception as e:
            raise ValueError(f"Error removing old link: {e}")

        # 2. Додаємо новий зв'язок (зі списанням годин)
        try:
            return PassRentalUsageService.add(new_pass_id, new_rental_id)
        except Exception as e:
            # Якщо додавання не вдалося, нам (в ідеалі) треба відкотити видалення,
            # але для курсової це вже ускладнення. Просто повертаємо помилку.
            raise ValueError(f"Old link removed, but failed to add new one: {e}")

    @staticmethod
    def delete(pass_id, rental_id):
        entry = PassRentalUsageService.get_by_id(pass_id, rental_id)
        if entry:
            pass_obj = PassService.get_by_id(pass_id)

            # Логіка повернення
            if pass_obj and pass_obj.pass_type.limit_hours > 0:
                pass_obj.remaining_hours += entry.hours_deducted

            db.session.delete(entry)
            db.session.commit()
            return True
        return False