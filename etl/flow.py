from prefect import flow
import postgres_credentials
import psycopg2
import etl_attendance
import etl_transcripts
import etl_gpa

def pg_connect():
    print('Connecting to postgres')
    conn = psycopg2.connect(
            database = postgres_credentials.database,
            user = postgres_credentials.user,
            password = postgres_credentials.password,
            host = postgres_credentials.host,
            port = postgres_credentials.port
            )

    return conn

@flow
def run_attendance():
    conn = pg_connect()
    etl_attendance.run_etl(conn)
    conn.commit
    conn.close()

@flow
def run_transcripts():
    conn = pg_connect()
    etl_transcripts.run_etl(conn)
    etl_gpa.run_etl(conn)
    conn.commit
    conn.close()
  
if __name__ == "__main__":
    run_attendance.serve(name="run_attendance",
    interval=86400)
	
    run_transcripts.serve(name="run_transcripts",
	interval=86400)
	