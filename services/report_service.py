from models import db
from models.client import Client
from models.passes import Pass
from models.pass_type import PassType
from sqlalchemy import desc # Для сортування

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

    # --- Тут пізніше можна буде додати методи для інших запитів ---
    # def get_most_rented_equipment_weekly(self, start_date, end_date): ...
    # def get_equipment_count_by_type_daily(self, date_): ...
    # ... і так далі для запитів 2-10