import sqlite3


class TaskRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def insert_running(self, task_id: str, task_name: str, prompt: str, started_at: str) -> None:
        self.conn.execute(
            """
            INSERT INTO tasks (id, task_name, prompt, status, started_at)
            VALUES (?, ?, ?, 'running', ?)
            """,
            (task_id, task_name, prompt, started_at),
        )

    def mark_completed(self, task_id: str, ended_at: str, result: str) -> None:
        self.conn.execute(
            """
            UPDATE tasks
            SET status = 'completed', ended_at = ?, result = ?, error = NULL
            WHERE id = ?
            """,
            (ended_at, result, task_id),
        )

    def mark_failed(self, task_id: str, ended_at: str, error: str) -> None:
        self.conn.execute(
            """
            UPDATE tasks
            SET status = 'failed', ended_at = ?, result = NULL, error = ?
            WHERE id = ?
            """,
            (ended_at, error, task_id),
        )

    def get(self, task_id: str) -> sqlite3.Row | None:
        return self.conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
