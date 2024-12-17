import os
import json
import sqlite3
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns

class WebJourneyLogger:
    def __init__(self, db_path="data/learning_journey.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()

    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    content TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    description TEXT,
                    difficulty TEXT
                )
            ''')
        print("Database initialized.")

    def scrape_tutorials(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        tutorials = []
        for tutorial in soup.select('.tutorial-item'):  # Update selector based on the website's structure
            title = tutorial.select_one('.title').text.strip()
            description = tutorial.select_one('.description').text.strip()
            difficulty = tutorial.select_one('.difficulty').text.strip()

            tutorials.append((title, description, difficulty))

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT INTO progress (title, description, difficulty)
                VALUES (?, ?, ?)
            ''', tutorials)

        print(f"Scraped and saved {len(tutorials)} tutorials.")

    def log_daily_learning(self, content):
        date = datetime.now().strftime("%Y-%m-%d")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO daily_logs (date, content)
                VALUES (?, ?)
            ''', (date, content))

        print("Daily log saved.")

    def analyze_logs(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT content FROM daily_logs')
            logs = cursor.fetchall()

        issues = {}
        for log in logs:
            words = log[0].split()
            for word in words:
                if word not in issues:
                    issues[word] = 0
                issues[word] += 1

        return issues

    def visualize_progress(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT date, content FROM daily_logs')
            logs = cursor.fetchall()

        dates = [log[0] for log in logs]
        counts = [len(log[1].split()) for log in logs]

        sns.barplot(x=dates, y=counts)
        plt.xticks(rotation=45)
        plt.title('Learning Progress Over Time')
        plt.xlabel('Date')
        plt.ylabel('Word Count')
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    logger = WebJourneyLogger()

    print("Choose an option:")
    print("1. Scrape tutorials")
    print("2. Log daily learning")
    print("3. Analyze logs")
    print("4. Visualize progress")

    choice = input("Enter your choice: ")

    if choice == "1":
        url = input("Enter the URL to scrape tutorials: ")
        logger.scrape_tutorials(url)
    elif choice == "2":
        content = input("Enter your daily learning log: ")
        logger.log_daily_learning(content)
    elif choice == "3":
        issues = logger.analyze_logs()
        print("Most common words/issues:", issues)
    elif choice == "4":
        logger.visualize_progress()
    else:
        print("Invalid choice.")
