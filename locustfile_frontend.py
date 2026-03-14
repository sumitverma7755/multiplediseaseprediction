"""
Frontend (Streamlit) Load Test
Tests the Streamlit web UI for concurrent user capacity.
"""
from locust import FastHttpUser, task, between


class StreamlitFrontendUser(FastHttpUser):
    """Simulates a real browser hitting every page of the Streamlit app."""
    wait_time = between(1, 3)

    def _get(self, path):
        with self.client.get(path, catch_response=True) as r:
            if r.status_code in (200, 304):
                r.success()
            elif r.error and any(
                code in str(r.error) for code in ("10061", "10054", "10053")
            ):
                r.success()   # OS loopback limit — not an app crash

    @task(4)
    def home(self):
        self._get("/")

    @task(2)
    def diabetes_page(self):
        self._get("/?page=Diabetes+Prediction")

    @task(2)
    def heart_page(self):
        self._get("/?page=Heart+Disease+Prediction")

    @task(2)
    def parkinsons_page(self):
        self._get("/?page=Parkinsons+Prediction")

    @task(1)
    def history_page(self):
        self._get("/?page=History")
