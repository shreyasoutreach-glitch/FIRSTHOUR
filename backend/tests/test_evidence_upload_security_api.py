"""
API-level regression test for the evidence-upload path-traversal fix.
Exercises the real /evidence/upload endpoint end-to-end (not just the
sanitizer function in isolation) and asserts the file that actually lands
on disk is contained inside EVIDENCE_STORAGE_DIR no matter what filename
the client sends.
"""
import io
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.tenancy import TenantScopedSession, tenant_scope
from app.main import app
import app.api.routes_evidence as routes_evidence
from app.models import entities as m

TEST_TENANT = "TEN_SEC_TEST"
TEST_TOKEN = "test_token_investigator"


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "upload_security_test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, class_=TenantScopedSession)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    storage_dir = tmp_path / "evidence_storage"
    storage_dir.mkdir()
    monkeypatch.setattr(routes_evidence.settings, "evidence_storage_dir", str(storage_dir))

    db = TestingSessionLocal()
    db.add(m.Tenant(id=TEST_TENANT, name="Security Test Tenant"))
    db.commit()
    with tenant_scope(db, TEST_TENANT):
        db.add(m.User(id="USR_SEC_INV", email="investigator@test.demo", display_name="Investigator",
                      role="INVESTIGATOR", api_token=TEST_TOKEN))
        db.add(m.Merchant(id="MER_SEC", name="Security Test Co", category="retail"))
        db.commit()
    db.close()

    with TestClient(app) as c:
        yield c, storage_dir
    app.dependency_overrides.clear()


def _auth_headers() -> dict:
    return {"Authorization": f"Bearer {TEST_TOKEN}"}


def _all_files_under(base_dir) -> list[str]:
    found = []
    for root, _dirs, files in os.walk(base_dir):
        for f in files:
            found.append(os.path.join(root, f))
    return found


TRAVERSAL_FILENAMES = [
    "../../../../etc/cron.d/evil",
    "..\\..\\..\\evil.txt",
    "/etc/passwd",
    "C:\\Windows\\System32\\evil.dll",
    "....//....//....//evil.sh",
]


@pytest.mark.parametrize("malicious_filename", TRAVERSAL_FILENAMES)
def test_traversal_filename_cannot_escape_storage_dir(client, malicious_filename):
    api_client, storage_dir = client
    project_root_marker = storage_dir.parent  # anything written outside storage_dir would land here or above

    resp = api_client.post(
        "/evidence/upload",
        data={"merchant_id": "MER_SEC", "incident_id": "", "source_label": "upload"},
        files={"file": (malicious_filename, io.BytesIO(b"malicious content"), "text/plain")},
        headers=_auth_headers(),
    )

    # The upload must either succeed with a neutralized filename, or be
    # rejected outright -- it must never write outside storage_dir.
    assert resp.status_code in (200, 400)

    written_files = _all_files_under(storage_dir)
    for f in written_files:
        resolved = os.path.realpath(f)
        assert resolved.startswith(os.path.realpath(str(storage_dir)) + os.sep), (
            f"File escaped storage dir: {resolved}"
        )

    # Confirm nothing was written directly into storage_dir's parent either
    # (i.e. no sibling file matching the malicious basename appeared there).
    parent_only_files = [
        f for f in os.listdir(project_root_marker)
        if os.path.isfile(os.path.join(project_root_marker, f))
    ]
    assert "evil" not in parent_only_files and "passwd" not in parent_only_files


def test_normal_filename_still_works_end_to_end(client):
    api_client, storage_dir = client
    resp = api_client.post(
        "/evidence/upload",
        data={"merchant_id": "MER_SEC", "incident_id": "", "source_label": "whatsapp"},
        files={"file": ("whatsapp_export.txt", io.BytesIO(b"Rs 50,000 to Test Vendor"), "text/plain")},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["filename"] == "whatsapp_export.txt"
    assert body["extraction_status"] == "text_ready"

    written_files = _all_files_under(storage_dir)
    assert any("whatsapp_export.txt" in f for f in written_files)
    for f in written_files:
        resolved = os.path.realpath(f)
        assert resolved.startswith(os.path.realpath(str(storage_dir)) + os.sep)


def test_traversal_filename_response_filename_is_sanitized(client):
    api_client, _storage_dir = client
    resp = api_client.post(
        "/evidence/upload",
        data={"merchant_id": "MER_SEC", "incident_id": "", "source_label": "upload"},
        files={"file": ("../../../../etc/cron.d/evil", io.BytesIO(b"x"), "text/plain")},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert ".." not in body["filename"]
    assert "/" not in body["filename"]
    assert body["filename"] == "evil"
