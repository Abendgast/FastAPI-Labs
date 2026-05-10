from locust import HttpUser, task, between

class APIUser(HttpUser):
    # Імітація поведінки реального користувача (пауза від 1 до 3 секунд між діями)
    wait_time = between(1, 3)

    @task
    def get_books(self):
        """
        Тестуємо ендпоінт отримання списку книг.
        Завдання вимагає тестування ендпоінту без Rate limiter.
        Використовуємо /books
        """
        with self.client.get("/books", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status code: {response.status_code}")
