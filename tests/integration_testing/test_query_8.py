import pytest
from models import db

from services.equipment_type_service import EquipmentTypeService
from services.tariff_service import TariffService

from services.report_service import ReportService

pytestmark = pytest.mark.usefixtures("app_context")


@pytest.fixture(scope='function')
def init_database(app_context):
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()


@pytest.fixture(scope='function')
def report_service():
    return ReportService()


@pytest.fixture(scope='function')
def equipment_type_service():
    return EquipmentTypeService()


@pytest.fixture(scope='function')
def tariff_service():
    return TariffService()


@pytest.fixture(scope='function')
def populate_db_for_query8(init_database, equipment_type_service, tariff_service):
    et_skis = equipment_type_service.add(name="Skis", description="Standard skis")
    et_board = equipment_type_service.add(name="Snowboard", description="All-mountain board")
    et_helmet = equipment_type_service.add(name="Helmet", description="Safety helmet")
    et_poles = equipment_type_service.add(name="Poles", description="Ski poles")

    tariff_service.add(et_skis.id, 200, 1000, 10)
    tariff_service.add(et_board.id, 300, 1200, 20)
    tariff_service.add(et_helmet.id, 100, 400, 0)

    return {
        "et_skis_name": et_skis.name,
        "et_board_name": et_board.name,
        "et_helmet_name": et_helmet.name,
        "et_poles_name": et_poles.name
    }


class TestReport8EquipmentTariffs:

    @pytest.mark.usefixtures("populate_db_for_query8")
    def test_get_equipment_tariffs_success(self, report_service, populate_db_for_query8):
        results = report_service.get_equipment_tariffs_with_weekday_discount()

        assert len(results) == 3

        data_map = {r.equipment_type_name: r for r in results}

        helmet_data = data_map[populate_db_for_query8["et_helmet_name"]]
        assert helmet_data.base_price_hour == 100
        assert helmet_data.base_price_day == 400
        assert helmet_data.weekday_discount == 0

        skis_data = data_map[populate_db_for_query8["et_skis_name"]]
        assert skis_data.base_price_hour == 200
        assert skis_data.base_price_day == 1000
        assert skis_data.weekday_discount == 10

        board_data = data_map[populate_db_for_query8["et_board_name"]]
        assert board_data.base_price_hour == 300
        assert board_data.base_price_day == 1200
        assert board_data.weekday_discount == 20

        assert populate_db_for_query8["et_poles_name"] not in data_map

        assert results[0].equipment_type_name == "Helmet"
        assert results[1].equipment_type_name == "Skis"
        assert results[2].equipment_type_name == "Snowboard"

    def test_get_equipment_tariffs_no_data(self, report_service, init_database):
        results = report_service.get_equipment_tariffs_with_weekday_discount()

        assert len(results) == 0
        assert results == []