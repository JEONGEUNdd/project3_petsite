import mysql.connector
from mysql.connector import pooling


# ✅ DB 설정
db_config = {
    "host": "10.0.66.31",
    "user": "sejong",
    "password": "1234",
    "database": "board_db",
    "pool_size": 5,  # 동시 5개 연결 유지
    "autocommit": True  # ✅ 자동 커밋 설정 (연결이 유지되도록)
}

class DBManager:
    def __init__(self):
        self.pool = mysql.connector.pooling.MySQLConnectionPool(**db_config)

    def get_connection(self):
        """ 커넥션 풀에서 연결 가져오기 """
        return self.pool.get_connection()

    def execute_query(self, query, params=None):
        """INSERT, UPDATE, DELETE 실행"""
        connection = self.get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            print(f"📌 실행할 쿼리: {query}")  # ✅ 실행될 SQL 출력
            print(f"📌 전달된 파라미터: {params}")  # ✅ 전달된 값 확인

            cursor.execute(query, params)
            connection.commit()
            print("✅ 쿼리 실행 성공")  # ✅ 성공 로그 추가
        except mysql.connector.Error as error:
            print(f"🚨 쿼리 실행 실패: {error}")  # ✅ 실패 로그
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    def fetch_all(self, query, params=None):
        """SELECT 다중 조회"""
        connection = self.get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        except mysql.connector.Error as error:
            print(f"🚨 데이터 조회 실패: {error}")
            return []
        finally:
            cursor.close()
            connection.close()

    def fetch_one(self, query, params=None):
        """SELECT 단일 조회"""
        connection = self.get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            return cursor.fetchone()
        except mysql.connector.Error as error:
            print(f"🚨 데이터 조회 실패: {error}")
            return None
        finally:
            cursor.close()
            connection.close()

    def validate_login(self, userid, password):
        """로그인 검증 (비밀번호 평문 비교)"""
        query = "SELECT user_id, username, email, province, city, district, password FROM users WHERE email = %s"
        try:
            user = self.fetch_one(query, (userid,))
            if user and user['password'] == password:
                return True, {
                    "user_id": user["user_id"],
                    "username": user["username"],
                    "email": user["email"],
                    "province": user.get("province", ""),  
                    "city": user.get("city", ""),          
                    "district": user.get("district", "")   
                }
            else:
                return False, None
        except Exception as e:
            print(f"🚨 로그인 검증 중 오류 발생: {e}")
            return False, None