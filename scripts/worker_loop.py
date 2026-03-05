import time
from app.workers.retry_worker import process_once as retry_once
from app.workers.escalation_worker import process_once as escalate_once


def main():
    while True:
        r = retry_once()
        e = escalate_once()
        print({"retry": r, "escalation": e})
        time.sleep(60)


if __name__ == "__main__":
    main()
