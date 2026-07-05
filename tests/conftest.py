"""Fixtures compartidas de pytest.

Cada test corre contra una base de datos SQLite **temporal y limpia**, para que
no dependan del orden de ejecución ni dejen basura entre corridas.
"""
import os
import tempfile

import pytest

# La ruta de la DB se lee al importar la app, así que la fijamos ANTES del import.
_TMP_DB = os.path.join(tempfile.gettempdir(), "cc63d_test_incidents.db")
os.environ["DATABASE_PATH"] = _TMP_DB
# El endpoint /work falla aleatoriamente; en los tests lo queremos determinista.
os.environ["FLAKY_ERROR_RATE"] = "0"

import app as appmodule  # noqa: E402  (debe ir tras fijar las env vars)


@pytest.fixture
def client():
    # DB fresca por test: borramos el archivo y recreamos el schema.
    if os.path.exists(_TMP_DB):
        os.remove(_TMP_DB)
    with appmodule.app.app_context():
        appmodule.init_db()
    appmodule.app.config["TESTING"] = True
    with appmodule.app.test_client() as c:
        yield c


def crear_servicio(client, name="payments-api", team="payments"):
    """Helper: crea un servicio y devuelve su id."""
    resp = client.post("/services", json={"name": name, "team": team})
    return resp.get_json()["id"]
