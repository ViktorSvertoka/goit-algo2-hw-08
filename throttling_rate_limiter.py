import time
from typing import Dict
import random
from colorama import Fore, init, Style


class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_requests: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        if user_id in self.user_requests:
            while (
                self.user_requests[user_id]
                and self.user_requests[user_id][0] <= current_time - self.window_size
            ):
                self.user_requests[user_id].popleft()
            if not self.user_requests[user_id]:
                del self.user_requests[user_id]

    def can_send_message(self, user_id: str) -> bool:
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        return len(self.user_requests.get(user_id, [])) < self.max_requests


class ThrottlingRateLimiter:
    def __init__(self, min_interval: float = 10.0):
        self.min_interval = min_interval
        self.last_message_time: Dict[str, float] = {}

    def can_send_message(self, user_id: str) -> bool:
        last_time = self.last_message_time.get(user_id, 0)
        return (time.time() - last_time) >= self.min_interval

    def record_message(self, user_id: str) -> bool:
        if self.can_send_message(user_id):
            self.last_message_time[user_id] = time.time()
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        last_time = self.last_message_time.get(user_id, 0)
        return max(0, self.min_interval - (time.time() - last_time))


def test_throttling_limiter():
    init(autoreset=True)

    limiter = ThrottlingRateLimiter(min_interval=10.0)

    print(
        Fore.CYAN
        + "\n=== Симуляція потоку повідомлень (Throttling) ==="
        + Style.RESET_ALL
    )
    print(" ")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        if result:
            status = f"{Fore.GREEN}✓"
        else:
            status = f"{Fore.RED}× (очікування {wait_time:.1f}с)"

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | {status}")

        time.sleep(random.uniform(0.1, 1.0))

    print(Fore.YELLOW + "\nОчікуємо 10 секунд..." + Style.RESET_ALL)
    time.sleep(10)

    print(
        Fore.CYAN
        + "\n=== Нова серія повідомлень після очікування ==="
        + Style.RESET_ALL
    )
    print(" ")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        if result:
            status = f"{Fore.GREEN}✓"
        else:
            status = f"{Fore.RED}× (очікування {wait_time:.1f}с)"

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | {status}")
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_throttling_limiter()
