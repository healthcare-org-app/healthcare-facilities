from app.routes import RESOURCE


def test_crud(client, svc):
    r = client.post(f"/api/{RESOURCE}/", json={"name": "test"})
    assert r.status_code == 201, r.data
    rid = r.get_json()["id"]

    r = client.get(f"/api/{RESOURCE}/{rid}")
    assert r.status_code == 200

    r = client.patch(f"/api/{RESOURCE}/{rid}", json={"name": "updated"})
    assert r.status_code == 200
    assert r.get_json()["name"] == "updated"

    r = client.delete(f"/api/{RESOURCE}/{rid}")
    assert r.status_code == 200

    r = client.get(f"/api/{RESOURCE}/")
    body = r.get_json()
    assert body["count"] >= 1


def test_get_missing(client):
    r = client.get(f"/api/{RESOURCE}/999999")
    assert r.status_code == 404


def test_audit_emitted_on_create(client, svc):
    client.post(f"/api/{RESOURCE}/", json={"name": "audit-me"})
    topics = [t for t, _, _ in svc.bus.published]
    assert "audit.event" in topics


class _FakeResponse:
    def __init__(self, status_code, body):
        self.status_code = status_code
        self._body = body
        self.text = str(body)

    def json(self):
        return self._body


class _FakeDemographicsClient:
    def __init__(self, response):
        self._response = response
        self.calls = []

    def post(self, path, json=None):
        self.calls.append((path, json))
        if isinstance(self._response, Exception):
            raise self._response
        return self._response


def test_create_with_address_gets_geocoded(client, svc):
    svc.clients["demographics-service"] = _FakeDemographicsClient(
        _FakeResponse(200, {"valid": True, "matched_address": "1 Main St, Springfield, IL, 62701",
                             "latitude": 39.8, "longitude": -89.6})
    )
    r = client.post(f"/api/{RESOURCE}/", json={"name": "test", "address": "1 Main St"})
    assert r.status_code == 201, r.data
    body = r.get_json()
    assert body["address_validated"] is True
    assert body["latitude"] == 39.8


def test_create_without_address_skips_geocoding(client, svc):
    demo = _FakeDemographicsClient(_FakeResponse(200, {"valid": True}))
    svc.clients["demographics-service"] = demo
    r = client.post(f"/api/{RESOURCE}/", json={"name": "test"})
    assert r.status_code == 201
    # No address given, so no geocoding call — filter-text (for `name`) is
    # unrelated and still happens.
    assert all(path != "/api/demographics/validate-address" for path, _ in demo.calls)


def test_create_demographics_service_down_is_best_effort(client, svc):
    from healthcare_common.http import ServiceUnavailable
    svc.clients["demographics-service"] = _FakeDemographicsClient(ServiceUnavailable("down"))
    r = client.post(f"/api/{RESOURCE}/", json={"name": "test", "address": "1 Main St"})
    assert r.status_code == 201
    assert "address_validated" not in r.get_json()


def test_create_filters_name(client, svc):
    demo = _FakeDemographicsClient(_FakeResponse(200, {"filtered": "****"}))
    svc.clients["demographics-service"] = demo
    r = client.post(f"/api/{RESOURCE}/", json={"name": "damn"})
    assert r.status_code == 201
    assert r.get_json()["name"] == "****"
    assert ("/api/demographics/filter-text", {"text": "damn"}) in demo.calls


def test_create_filter_text_down_is_best_effort(client, svc):
    from healthcare_common.http import ServiceUnavailable
    svc.clients["demographics-service"] = _FakeDemographicsClient(ServiceUnavailable("down"))
    r = client.post(f"/api/{RESOURCE}/", json={"name": "test"})
    assert r.status_code == 201
    assert r.get_json()["name"] == "test"
