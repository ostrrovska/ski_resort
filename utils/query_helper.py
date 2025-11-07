import datetime
from models import db
from sqlalchemy.orm import Query
from sqlalchemy.exc import ArgumentError


class QueryHelper:
    """
    Цей клас надає статичні методи для застосування динамічного
    сортування та фільтрації до запитів SQLAlchemy.
    """

    @staticmethod
    def _get_column(models_map: dict, col_name: str):
        """
        Безпечно отримує атрибут колонки з однієї або кількох моделей.
        """
        for model_class in models_map.values():
            if hasattr(model_class, col_name):
                col = getattr(model_class, col_name)
                if hasattr(col, 'type'):
                    return col
        return None

    @staticmethod
    def apply_filters(query: Query, models_map: dict, filter_cols: list, filter_ops: list, filter_vals: list) -> Query:
        """
        Застосовує список фільтрів до об'єкта Query.
        """
        if not all([filter_cols, filter_ops, filter_vals]) or \
                len(filter_cols) != len(filter_ops) or len(filter_ops) != len(filter_vals):
            return query

        for col_name, op, val_str in zip(filter_cols, filter_ops, filter_vals):
            col = QueryHelper._get_column(models_map, col_name)

            if col is None:
                continue

            val = None
            try:
                if isinstance(col.type, db.Integer):
                    val = int(val_str)
                elif isinstance(col.type, db.Date):
                    val = datetime.datetime.strptime(val_str, "%Y-%m-%d").date()
                elif isinstance(col.type, db.Time):
                    val = datetime.datetime.strptime(val_str, "%H:%M:%S").time()
                elif isinstance(col.type, db.Boolean):
                    val = val_str.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(col.type, db.Enum):
                    val = val_str
                else:
                    val = val_str
            except (ValueError, TypeError):
                continue

            try:
                if op == 'eq':
                    query = query.filter(col == val)
                elif op == 'neq':
                    query = query.filter(col != val)
                elif op == 'gt':
                    query = query.filter(col > val)
                elif op == 'gte':
                    query = query.filter(col >= val)
                elif op == 'lt':
                    query = query.filter(col < val)
                elif op == 'lte':
                    query = query.filter(col <= val)
                elif op == 'like' and isinstance(col.type, db.String):
                    query = query.filter(col.ilike(f'%{val}%'))
                elif op == 'in' and isinstance(col.type, db.String):
                    query = query.filter(col == val)
            except ArgumentError:
                continue
        return query

    @staticmethod
    def apply_sorting(query: Query, models_map: dict, sort_by: str, sort_order: str) -> Query:
        """
        Застосовує сортування до об'єкта Query.
        """
        if sort_by:
            col = QueryHelper._get_column(models_map, sort_by)
            if col:
                if sort_order == 'desc':
                    query = query.order_by(col.desc())
                else:
                    query = query.order_by(col.asc())
        return query

    @staticmethod
    def get_all(model_class, sort_by=None, sort_order='asc',
                filter_cols=None, filter_ops=None, filter_vals=None,  # Новий стиль
                filter_by=None, filter_value=None):  # Старий стиль
        """
        Універсальний метод get_all, що підтримує обидва стилі фільтрації.
        Новий стиль (списки) має пріоритет, якщо надано.
        """
        query = model_class.query
        models_map = {model_class.__name__: model_class}

        # --- ОНОВЛЕНА ЛОГІКА ---

        # Перевіряємо, чи НЕ надані нові фільтри (filter_cols порожній або None)
        # І чи надані старі фільтри
        if (not filter_cols) and (filter_by and filter_value is not None):

            col = QueryHelper._get_column(models_map, filter_by)
            op = 'eq'  # (default)

            # Відтворюємо оригінальну логіку: 'like' для рядків, 'eq' для інших (int, date, etc)
            if col is not None and isinstance(col.type, db.String):
                op = 'like'

            # Конвертуємо старий стиль у новий
            filter_cols = [filter_by]
            filter_ops = [op]
            filter_vals = [filter_value]

        # --- КІНЕЦЬ ОНОВЛЕНОЇ ЛОГІКИ ---

        # Тепер ми гарантовано маємо або нові фільтри, або нічого
        query = QueryHelper.apply_filters(query, models_map, filter_cols, filter_ops, filter_vals)
        query = QueryHelper.apply_sorting(query, models_map, sort_by, sort_order)

        return query.all()