from datetime import timedelta, datetime

future = datetime.now() + timedelta(days=7)  # 7 days in the future
past = datetime.now() - timedelta(hours=2)  # 2 hours in the past
past_week = datetime.now() - timedelta(days=7)

if __name__ == '__main__':
    print(future)
    print(past_week)
