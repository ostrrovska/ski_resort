from models.saved_view import SavedView, db

class SavedViewService:

    @staticmethod
    def get_by_client_id(client_id):
        return SavedView.query.filter_by(client_id=client_id).all()

    @staticmethod
    def add(name, url, client_id):
        new_view = SavedView(name=name, url=url, client_id=client_id)
        db.session.add(new_view)
        db.session.commit()
        return new_view

    @staticmethod
    def delete(view_id, client_id):
        # Ensure a user can only delete their own views
        view_to_delete = SavedView.query.filter_by(id=view_id, client_id=client_id).first()
        if view_to_delete:
            db.session.delete(view_to_delete)
            db.session.commit()
            return True
        return False