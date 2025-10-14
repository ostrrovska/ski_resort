from models.equipment import Equipment, db
from models.equipment_type import EquipmentType
from services.equipment_type_service import EquipmentTypeService


class EquipmentService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_by=None, filter_value=None):
        query = Equipment.query
        sort_filter_options = {
            'id': Equipment.id,
            'type_id': Equipment.type_id,
            'model': Equipment.model,
            'is_available': Equipment.is_available
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
            elif isinstance(column.type, db.Boolean):
                processed_value = str(filter_value).lower() in ('true', 'on', '1', 'yes')
                query = query.filter(column == processed_value)
            else:
                query = query.filter(column.ilike(f'%{filter_value}%'))
        return query.all()

    @staticmethod
    def get_all_joined(sort_by=None, sort_order='asc', filter_by=None, filter_value=None):
        """
        Повертає список обладнання з об'єднаною інформацією про його тип.
        """
        query = db.session.query(Equipment, EquipmentType).join(EquipmentType, Equipment.type_id == EquipmentType.id)

        sort_filter_options = {
            'id': Equipment.id,
            'model': Equipment.model,
            'is_available': Equipment.is_available,
            'description': EquipmentType.description,
            'type_name': EquipmentType.name,
            'type_description': EquipmentType.description
        }

        if filter_by in sort_filter_options and filter_value is not None:
            column = sort_filter_options[filter_by]
            if isinstance(column.type, db.Boolean):
                processed_value = str(filter_value).lower() in ('true', 'on', '1', 'yes')
                query = query.filter(column == processed_value)
            elif isinstance(column.type, db.Integer):
                try:
                    query = query.filter(column == int(filter_value))
                except ValueError:
                    pass
            else:
                query = query.filter(column.ilike(f'%{filter_value}%'))

        if sort_by in sort_filter_options:
            column = sort_filter_options[sort_by]
            if sort_order == 'desc':
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())

        return query.all()

    @staticmethod
    def get_by_id(id):
        return Equipment.query.get(id)

    @staticmethod
    def add(type_id, model, is_available):
        equipment_type = EquipmentTypeService.get_by_id(type_id)
        if not equipment_type:
            raise ValueError(f"Type of equipment with ID {type_id} is not found.")

        new_equipment = Equipment(type_id, model, is_available)
        db.session.add(new_equipment)
        db.session.commit()
        return new_equipment

    @staticmethod
    def update(id, type_id, model, is_available):
        equipment = EquipmentService.get_by_id(id)
        if not equipment:
            return None

        equipment_type = EquipmentTypeService.get_by_id(type_id)
        if not equipment_type:
            raise ValueError(f"Type of equipment with ID {type_id} is not found.")

        equipment.type_id = type_id
        equipment.model = model
        equipment.is_available = is_available
        db.session.commit()
        return equipment

    @staticmethod
    def delete(id):
        equipment = EquipmentService.get_by_id(id)
        if equipment:
            db.session.delete(equipment)
            db.session.commit()
            return True
        return False
