# priority_inbox.py
# Python 3

import requests
import heapq
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

API_URL = "http://20.207.122.201/evaluation-service/notifications"

# Example token if required
TOKEN = os.getenv("AUTH_TOKEN")

# Weight mapping for notification type
TYPE_WEIGHT = {
    "placement": 5,
    "result": 4,
    "event": 3,
    "mid-sem": 2,
    "general": 1
}

TOP_N = 10


class Notification:
    def __init__(self, data):
        self.id = data["ID"]
        self.type = data["Type"]
        self.message = data["Message"]
        self.timestamp = datetime.strptime(
            data["Timestamp"],
            "%Y-%m-%d %H:%M:%S"
        )

    def priority_score(self):
        """
        Higher score => higher priority
        Priority based on:
        1. Type weight
        2. Recency
        """

        type_score = TYPE_WEIGHT.get(self.type.lower(), 0)

        # Convert timestamp into comparable integer
        recency_score = self.timestamp.timestamp()

        return (type_score, recency_score)

    def __lt__(self, other):
        return self.priority_score() < other.priority_score()

    def __repr__(self):
        return (
            f"[{self.type.upper()}] "
            f"{self.message} | "
            f"{self.timestamp}"
        )


def fetch_notifications():
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    response = requests.get(API_URL, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"API Error: {response.status_code}"
        )

    data = response.json()

    return [
        Notification(item)
        for item in data["notifications"]
    ]


def get_top_notifications(notifications, n=10):
    """
    Efficient approach:
    Maintain min heap of size n
    Time Complexity:
    O(N log n)
    """

    heap = []

    for notification in notifications:

        if len(heap) < n:
            heapq.heappush(heap, notification)

        else:
            if notification.priority_score() > heap[0].priority_score():
                heapq.heappop(heap)
                heapq.heappush(heap, notification)

    # Highest priority first
    return sorted(
        heap,
        key=lambda x: x.priority_score(),
        reverse=True
    )


if __name__ == "__main__":

    try:
        notifications = fetch_notifications()

        top_notifications = get_top_notifications(
            notifications,
            TOP_N
        )

        print("\nPRIORITY INBOX\n")

        for idx, notif in enumerate(top_notifications, start=1):
            print(f"{idx}. {notif}")

    except Exception as e:
        print("Error:", e)