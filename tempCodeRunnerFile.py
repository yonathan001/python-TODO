import mysql.connector
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  
        password="",  
        database="todo_db"  
    )

# Create tasks table
def create_tasks_table():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            task VARCHAR(255) NOT NULL,
            status BOOLEAN DEFAULT FALSE
        )
    """)
    db.commit()
    db.close()

# HTTP Server Class
class TodoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("index.html", "rb") as file:
                self.wfile.write(file.read())

        elif self.path == "/tasks":
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM tasks")
            tasks = cursor.fetchall()
            db.close()

            tasks_json = json.dumps([{"id": task[0], "task": task[1], "status": task[2]} for task in tasks])
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(tasks_json.encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length).decode("utf-8")
        data = parse_qs(post_data)

        # Handle adding a task
        if self.path == "/add":
            task_text = data.get("task", [""])[0]
            if task_text.strip():
                db = get_db_connection()
                cursor = db.cursor()
                cursor.execute("INSERT INTO tasks (task) VALUES (%s)", (task_text,))
                db.commit()
                db.close()

        # Handle completing a task
        elif self.path.startswith("/complete/"):
            try:
                task_id = int(self.path.split("/")[-1])  # Extract ID from URL
                db = get_db_connection()
                cursor = db.cursor()
                cursor.execute("UPDATE tasks SET status = TRUE WHERE id = %s", (task_id,))
                db.commit()
                db.close()
            except ValueError:
                self.send_response(400)
                self.end_headers()
                return

        # Handle deleting a task
        elif self.path.startswith("/delete/"):
            try:
                task_id = int(self.path.split("/")[-1])  # Extract ID from URL
                db = get_db_connection()
                cursor = db.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
                db.commit()
                db.close()
            except ValueError:
                self.send_response(400)
                self.end_headers()
                return

        # Redirect back to main page after action
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()
# Run the server
create_tasks_table()
server_address = ("", 8000)
httpd = HTTPServer(server_address, TodoHandler)
print("Server running at http://localhost:8000")
httpd.serve_forever()
