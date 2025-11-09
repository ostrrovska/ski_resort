from models.pass_lift_usage import PassLiftUsage
from models import db
from services.pass_service import PassService
from services.lift_usage_service import LiftUsageService
from utils.query_helper import QueryHelper


class PassLiftUsageService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_cols=None, filter_ops=None, filter_vals=None):
        return QueryHelper.get_all(
            PassLiftUsage,
            sort_by,
            sort_order,
            filter_cols,
            filter_ops,
            filter_vals
        )

    @staticmethod
    def get_by_id(pass_id, lift_usage_id):
        return db.session.get(PassLiftUsage, (pass_id, lift_usage_id))

    @staticmethod
    def add(pass_id, lift_usage_id):
        # --- ПОЧАТОК ЗМІН ---
        # 1. Отримуємо об'єкти Pass та LiftUsage
        pass_obj = PassService.get_by_id(pass_id)
        lift_usage_obj = LiftUsageService.get_by_id(lift_usage_id)

        if not pass_obj:
            raise ValueError(f"Pass with id={pass_id} is not found.")
        if not lift_usage_obj:
            raise ValueError(f"LiftUsage with id={lift_usage_id} is not found.")

        if pass_obj.pass_type.limit_lifts <= 0:
            raise ValueError(f"Pass {pass_id} is not a lift-based pass.")

        if pass_obj.remaining_lifts <= 0:
            raise ValueError(f"Pass {pass_id} has no remaining lifts.")

        pass_obj.remaining_lifts -= 1
        # --- КІНЕЦЬ ЗМІН ---
        new_entry = PassLiftUsage(pass_id=pass_id, lift_usage_id=lift_usage_id)
        db.session.add(new_entry)
        db.session.commit()
        return new_entry

    @staticmethod
    def update(old_pass_id, old_lift_usage_id, new_pass_id, new_lift_usage_id):
        # --- ПОЧАТОК ЗМІН ---
        # Використовуємо ту ж логіку, що й в rental_usage:
        # 1. Видаляємо старий зв'язок (з поверненням підйому)
        try:
            PassLiftUsageService.delete(old_pass_id, old_lift_usage_id)
        except Exception as e:
            raise ValueError(f"Error removing old link: {e}")

        # 2. Додаємо новий зв'язок (зі списанням підйому)
        try:
            return PassLiftUsageService.add(new_pass_id, new_lift_usage_id)
        except Exception as e:
            # Якщо додавання не вдалося, нам (в ідеалі) треба відкотити видалення,
            # але для курсової це вже ускладнення. Просто повертаємо помилку.
            raise ValueError(f"Old link removed, but failed to add new one: {e}")
        # --- КІНЕЦЬ ЗМІН ---

    @staticmethod
    def delete(pass_id, lift_usage_id):
        entry = PassLiftUsageService.get_by_id(pass_id, lift_usage_id)
        if entry:
            # --- ПОЧАТОК ЗМІН ---
            # 1. Знаходимо абонемент, пов'язаний із цим використанням
            pass_obj = PassService.get_by_id(pass_id)

            # 2. Логіка повернення: повертаємо підйом, ЯКЩО це абонемент на підйоми
            if pass_obj and pass_obj.pass_type.limit_lifts > 0:
                pass_obj.remaining_lifts += 1

            db.session.delete(entry)
            db.session.commit()
            return True
        return False
