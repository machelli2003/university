import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000/api/v1"


def send(method, path, body=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            return res.status, json.loads(res.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode()
        print(f"HTTP {exc.code} {method} {path}: {body}")
        raise


if __name__ == "__main__":
    print("1) Health check")
    status, body = send("GET", "/health")
    print(status, body)

    print("2) Login as applicant")
    status, auth = send("POST", "/auth/login", {"email": "applicant@test.com", "password": "Applicant123!"})
    print(status, auth)
    token = auth["access_token"]

    print("3) Check if applicant already has an application")
    try:
        status, application = send("POST", "/admissions/apply", {"phone": "0240000000", "first_name": "Kwame", "last_name": "Mensah", "email": "applicant@test.com"}, token)
        print(status, application)
    except urllib.error.HTTPError:
        print("Application exists or could not create. Fetching existing draft via /admissions if available is not implemented here.")
        application = None

    if application is None:
        print("Unable to create application; using sample existing app id from a previous run")
        # If the applicant already has a draft, use the id from the backend by listing applicants not implemented.
        raise SystemExit(1)

    print("4) Submit application")
    application_id = application["id"]
    status, submitted = send("POST", f"/admissions/{application_id}/submit", {
        "index_number": "12345678",
        "exam_year": 2025,
        "exam_type": "WASSCE",
        "programme_choices": [{"programme_id": "6a768b0ec221baf94140ce90", "choice_order": 1}],
    }, token)
    print(status, submitted)

    print("5) Submit applicant results")
    status, results_resp = send("POST", f"/admissions/{application_id}/results/submit", {
        "results": {"english": "B3", "mathematics": "A1", "science": "B2", "elective_1": "A2"}
    }, token)
    print(status, results_resp)

    print("6) Login as admissions officer")
    status, officer_auth = send("POST", "/auth/login", {"email": "officer@test.com", "password": "Officer123!"})
    print(status, officer_auth)
    officer_token = officer_auth["access_token"]

    print("7) Approve results")
    status, approve_resp = send("POST", f"/admissions/{application_id}/results/approve", {"aggregate": 7}, officer_token)
    print(status, approve_resp)

    print("8) Evaluate eligibility")
    status, eligibility = send("POST", f"/admissions/{application_id}/eligibility/evaluate", None, officer_token)
    print(status, eligibility)

    print("9) Rank applicants")
    status, ranking = send("POST", f"/admissions/programmes/6a768b0ec221baf94140ce90/rank", None, officer_token)
    print(status, ranking)

    print("10) Allocate programmes")
    status, allocation = send("POST", "/admissions/allocate", None, officer_token)
    print(status, allocation)

    print("11) Publish offers")
    status, publish = send("POST", "/admissions/offers/publish", None, officer_token)
    print(status, publish)
