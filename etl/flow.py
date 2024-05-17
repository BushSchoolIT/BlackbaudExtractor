from prefect import flow, serve, task
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

@task
def transcripts_task(conn):
    etl_transcripts.run_etl(conn)
    conn.commit

@task
def gpa_task(conn):
    etl_gpa.run_etl(conn)
    conn.commit

@flow
def run_attendance():
    conn = pg_connect()
    etl_attendance.run_etl(conn)
    conn.commit
    conn.close()

@flow
def run_transcripts():
    conn = pg_connect()
    transcripts_task(conn)
    gpa_task(conn)
    conn.close()
  
if __name__ == "__main__":
    attendance_deploy = run_attendance.to_deployment(name="run_attendance",
    interval=86400)
    transcripts_deploy = run_transcripts.to_deployment(name="run_transcripts",
	interval=86400)
    serve(attendance_deploy, transcripts_deploy)
