from locust import HttpUser,task,between

class WebSiteUser(HttpUser):
    wait_time = between(5,35)
    @task(1)
    def view(self):
        self.client.get("/get/proposals")