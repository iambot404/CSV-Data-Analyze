import io
import json
import pytest
from api.index import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_homepage(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"SynapseCSV" in res.data
    assert b"AI Data Analyzer" in res.data

def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["max_upload_size_mb"] == 10

def test_auth_workflow(client):
    email = f"test_{int(pytest.importorskip('time').time())}@example.com"
    pwd = "secretpassword123"

    # Register
    reg_res = client.post("/api/auth/register", json={
        "email": email,
        "password": pwd,
        "full_name": "Test User"
    })
    assert reg_res.status_code == 201
    reg_data = reg_res.get_json()
    assert "token" in reg_data

    # Login
    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": pwd
    })
    assert login_res.status_code == 200
    token = login_res.get_json()["token"]

    # Verify Current User
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.get_json()
    assert me_data["authenticated"] is True
    assert me_data["user"]["email"] == email

def test_samples_and_query(client):
    # 1. List samples
    samples_res = client.get("/api/samples")
    assert samples_res.status_code == 200
    samples = samples_res.get_json()["samples"]
    assert len(samples) >= 3

    # 2. Load ecommerce sample
    load_res = client.post("/api/samples/ecommerce/load")
    assert load_res.status_code == 200
    data = load_res.get_json()
    assert data["success"] is True
    analysis = data["analysis"]
    assert analysis["row_count"] > 0
    assert "ai_insights" in analysis
    assert "charts" in analysis
    analysis_id = analysis["id"]

    # 3. Ask AI a question about this dataset
    query_res = client.post(f"/api/analysis/{analysis_id}/query", json={
        "question": "Which customer segment has the highest profit?"
    })
    assert query_res.status_code == 200
    q_data = query_res.get_json()
    assert q_data["success"] is True
    assert len(q_data["answer"]) > 0

def test_upload_csv_file(client):
    csv_content = b"department,employees,budget\nEngineering,50,500000\nMarketing,20,200000\nSales,35,350000\n"
    data = {
        "file": (io.BytesIO(csv_content), "departments.csv")
    }
    res = client.post("/api/upload", data=data, content_type="multipart/form-data")
    assert res.status_code == 200
    res_data = res.get_json()
    assert res_data["success"] is True
    assert res_data["analysis"]["column_count"] == 3
    assert res_data["analysis"]["row_count"] == 3

def test_upload_empty_csv(client):
    data = {
        "file": (io.BytesIO(b""), "empty.csv")
    }
    res = client.post("/api/upload", data=data, content_type="multipart/form-data")
    assert res.status_code in [400, 422]

def test_history_endpoint(client):
    res = client.get("/api/history")
    assert res.status_code == 200
    assert "history" in res.get_json()
