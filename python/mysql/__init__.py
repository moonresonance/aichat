from http.client import HTTPException

from mysql.connector import pooling, Error


class MySQLPool:
    def __init__(self, host="localhost", user="root", password="20031224", database="aichat", pool_name="mysql_pool", pool_size=5):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.pool_name = pool_name
        self.pool_size = pool_size
        self.pool = pooling.MySQLConnectionPool(
            pool_name=self.pool_name,
            pool_size=self.pool_size,
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    # -----------------------------
    def get_last_five_chats(self, user_id: str, session_id: str):
        try:
            # 从连接池中获取一个连接
            conn = self.pool.get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
            SELECT role, content FROM chat
            WHERE user_id = %s AND session_id = %s
            ORDER BY id DESC LIMIT 10
            """
            cursor.execute(query, (user_id, session_id))
            rows = cursor.fetchall()

            # 构造上下文消息列表
            context = [{"role": row["role"], "content": row["content"]} for row in rows]

            return context

        except Error as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

        finally:
            # 释放资源（非常重要）
            if cursor:
                cursor.close()
            if conn:
                conn.close()  # 实际上是把连接放回连接池

    def get_propmt(self, user_id: str, session_id: str):
        try:
            # 从连接池中获取一个连接
            conn = self.pool.get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
            SELECT prompt FROM prompt
            WHERE user_id = %s AND session_id = %s
            ORDER BY id DESC LIMIT 1
            """
            cursor.execute(query, (user_id, session_id))
            row = cursor.fetchone()

            # 构造上下文消息列表
            prompt = row["prompt"] if row else "你是个智能助手"

            return prompt

        except Error as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

        finally:
            # 释放资源（非常重要）
            if cursor:
                cursor.close()
            if conn:
                conn.close()  # 实际上是把连接放回连接池
    def add_propmt(self, user_id: str, session_id: str, prompt: str):
        try:
            # 从连接池中获取一个连接
            conn = self.pool.get_connection()
            cursor = conn.cursor()

            query = """
            INSERT INTO prompt (user_id, session_id, prompt)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (user_id, session_id, prompt))
            conn.commit()

        except Error as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

        finally:
            # 释放资源（非常重要）
            if cursor:
                cursor.close()
            if conn:
                conn.close()  # 实际上是把连接放回连接池

