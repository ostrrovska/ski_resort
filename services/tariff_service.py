from models import db
from models.tariff import Tariff
from services.equipment_type_service import EquipmentTypeService

class TariffService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_by=None, filter_value=None):
        query = Tariff.query
        sort_filter_options = {
            'id': Tariff.id,
            'equipment_type_id': Tariff.equipment_type_id,
            'price_per_hour': Tariff.price_per_hour,
            'price_per_day': Tariff.price_per_day,
            'weekday_discount': Tariff.weekday_discount
        }
        if sort_by in sort_filter_options:
            if sort_order == 'desc':
                query = query.order_by(sort_filter_options[sort_by].desc())
            else:
                query = query.order_by(sort_filter_options[sort_by])

        if filter_by in sort_filter_options and filter_value:
            column = sort_filter_options[filter_by]
            if isinstance(column.type, db.Integer):
                query = query.filter(column == int(filter_value))
            else:
                query = query.filter(column.ilike(f'%{filter_value}%'))
        return query.all()

    @staticmethod
    def get_by_id(id):
        return Tariff.query.get(id)

    @staticmethod
    def add(equipment_type_id, price_per_hour, price_per_day, weekday_discount):
        equipment_type = EquipmentTypeService.get_by_id(equipment_type_id)
        if not equipment_type:
            raise ValueError(f"Type of equipment with ID {equipment_type_id} is not found.")

        new_tariff = Tariff(equipment_type_id, price_per_hour, price_per_day, weekday_discount)
        db.session.add(new_tariff)
        db.session.commit()
        return new_tariff

    @staticmethod
    def update(id, equipment_type_id, price_per_hour, price_per_day, weekday_discount):
        tariff = TariffService.get_by_id(id)
        if not tariff:
            return None

        equipment_type = EquipmentTypeService.get_by_id(equipment_type_id)
        if not equipment_type:
            raise ValueError(f"Type of equipment with ID {equipment_type_id} is not found.")

        tariff.equipment_type_id = equipment_type_id
        tariff.price_per_hour = price_per_hour
        tariff.price_per_day = price_per_day
        tariff.weekday_discount = weekday_discount
        db.session.commit()
        return tariff

    @staticmethod
    def delete(id):
        tariff = TariffService.get_by_id(id)
        if tariff:
            db.session.delete(tariff)
            db.session.commit()
            return True
        return False