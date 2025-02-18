from http.server import SimpleHTTPRequestHandler, HTTPServer
import mysql.connector
import urllib.parse

HOST = "localhost"
PORT = 8080

# Database Connection Function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Change this if necessary
        password="",  # Add your MySQL password
        database="todo_db"
    )

class TodoHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM tasks")
            tasks = cursor.fetchall()
            db.close()

            html = "<html><head><title>To-Do App</title><style>body { font-family: Arial, sans-serif; text-align: center; margin: 50px;} table { width: 50%; margin: auto; border-collapse: collapse; } th, td { padding: 10px; border: 1px solid #ddd; } th { background-color: #4CAF50; color: white; } .completed { text-decoration: line-through; color: gray; }</style></head><body>"
            html += "<h1>To-Do List</h1>"
            html += '<form action="/add" method="POST"><input type="text" name="task" required><button type="submit">Add Task</button></form>'
            html += "<table><tr><th>Task</th><th>Action</th></tr>"

            for task in tasks:
                html += f"<tr><td class='{ 'completed' if task[2] else '' }'>{task[1]}</td>"
                html += f"<td><a href='/complete/{task[0]}'>✔️ Complete</a> <a href='/delete/{task[0]}'>❌ Delete</a></td></tr>"

            html += "</table></body></html>"
            self.wfile.write(html.encode("utf-8"))

        elif self.path.startswith("/complete/"):
            task_id = self.path.split("/")[-1]
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("UPDATE tasks SET status = TRUE WHERE id = %s", (task_id,))
            db.commit()
            db.close()

            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()

        elif self.path.startswith("/delete/"):
            task_id = self.path.split("/")[-1]
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            db.commit()
            db.close()

            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()

        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/add":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length).decode("utf-8")
            params = urllib.parse.parse_qs(post_data)
            task = params.get("task", [""])[0]

            if task:
                db = get_db_connection()
                cursor = db.cursor()
                cursor.execute("INSERT INTO tasks (task) VALUES (%s)", (task,))
                db.commit()
                db.close()

            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()

# Start the Server
server = HTTPServer((HOST, PORT), TodoHandler)
print(f"Server running at http://{HOST}:{PORT}/")
server.serve_forever()
