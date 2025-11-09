from models import db
from models.equipment_type import EquipmentType
from models.tariff import Tariff
from services.equipment_type_service import EquipmentTypeService
from utils.query_helper import QueryHelper


class TariffService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_by=None, filter_value=None,
                filter_cols=None, filter_ops=None, filter_vals=None):
        return QueryHelper.get_all(
            Tariff,
            sort_by,
            sort_order,
            filter_cols,
            filter_ops,
            filter_vals,
            filter_by=filter_by,
            filter_value=filter_value,
        )

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

    @staticmethod
    def get_all_joined(sort_by='type_name', sort_order='asc'):
        """
        Повертає список тарифів з об'єднаною інформацією про тип обладнання.
        """
        query = db.session.query(Tariff, EquipmentType).join(
            EquipmentType, Tariff.equipment_type_id == EquipmentType.id
        )

        sort_options = {
            'type_name': EquipmentType.name,
            'price_per_hour': Tariff.price_per_hour,
            'price_per_day': Tariff.price_per_day,
            'weekday_discount': Tariff.weekday_discount
        }

        column = sort_options.get(sort_by, EquipmentType.name)
        if sort_order == 'desc':
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())

        return query.all()