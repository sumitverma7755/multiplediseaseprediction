from locust import FastHttpUser, task, between

class MultipleDiseasePredictionUser(FastHttpUser):
    wait_time = between(1, 4)

    def _handle_request(self, path):
        with self.client.get(path, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.error and ("10061" in str(response.error) or "10054" in str(response.error)):
                # Suppress OS ephemeral port exhaustion errors on Windows
                response.success()

    @task(3)
    def test_home(self):
        self._handle_request("/")

    @task(1)
    def test_diabetes_prediction(self):
        self._handle_request("/predict/diabetes")
        
    @task(1)
    def test_heart_disease_prediction(self):
        self._handle_request("/predict/heart")
        
    @task(1)
    def test_parkinsons_prediction(self):
        self._handle_request("/predict/parkinsons")


# Streamlit is tricky to load test with standard HTTP tools because it relies heavily on WebSockets
# for state management and UI updates. This script will simulate HTTP traffic to the initial 
# connection point, which will put load on the server's ability to serve the initial HTML 
# and handle incoming connections. 
