from models.equipment_type import EquipmentType, db
from utils.query_helper import QueryHelper


class EquipmentTypeService:

    @staticmethod
    def get_all(filter_cols=None, filter_ops=None, filter_vals=None,sort_by=None, sort_order='asc',
                filter_by=None, filter_value=None):
        return QueryHelper.get_all(
            EquipmentType,
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
        return EquipmentType.query.get(id)

    @staticmethod
    def add(name, description):
        new_equipment_type = EquipmentType(name, description)
        db.session.add(new_equipment_type)
        db.session.commit()
        return new_equipment_type

    @staticmethod
    def update(id, name, description):
        equipment_type = EquipmentTypeService.get_by_id(id)
        if equipment_type:
            equipment_type.name = name
            equipment_type.description = description
            db.session.commit()
            return True
        return False

    @staticmethod
    def delete(id):
        equipment_type = EquipmentTypeService.get_by_id(id)
        if equipment_type:
            db.session.delete(equipment_type)
            db.session.commit()
            return True
        return False