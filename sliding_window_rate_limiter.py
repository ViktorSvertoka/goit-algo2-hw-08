import random
from typing import Dict
import time
from collections import deque
from colorama import Fore, Style


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

    def record_message(self, user_id: str) -> bool:
        if self.can_send_message(user_id):
            if user_id not in self.user_requests:
                self.user_requests[user_id] = deque()
            self.user_requests[user_id].append(time.time())
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        if user_id not in self.user_requests or not self.user_requests[user_id]:
            return 0.0
        return max(
            0.0, self.window_size - (time.time() - self.user_requests[user_id][0])
        )


def test_rate_limiter():
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    print(Fore.CYAN + "\n=== Симуляція потоку повідомлень ===" + Style.RESET_ALL)
    print(" ")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{Fore.GREEN + '✓' if result else Fore.RED + f'× (очікування {wait_time:.1f}с)'}"
            + Style.RESET_ALL
        )
        time.sleep(random.uniform(0.1, 1.0))

    print(Fore.YELLOW + "\nОчікуємо 4 секунди..." + Style.RESET_ALL)
    time.sleep(4)

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
        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{Fore.GREEN + '✓' if result else Fore.RED + f'× (очікування {wait_time:.1f}с)'}"
            + Style.RESET_ALL
        )
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()
