from models.equipment_type import EquipmentType, db

class EquipmentTypeService:

    @staticmethod
    def get_all(sort_by = None, sort_order = 'asc', filter_by = None, filter_value = None):
        query = EquipmentType.query
        sort_filter_options = {
            'id': EquipmentType.id,
            'name': EquipmentType.name,
            'description': EquipmentType.description
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