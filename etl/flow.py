import os
import sys
import io
import subprocess
from prefect import flow, serve, task
import postgres_credentials
import psycopg2
import etl_attendance
import etl_transcripts
import etl_gpa
import etl_enrollment
import etl_transcript_comments
import etl_parents
from prefect.task_runners import SequentialTaskRunner

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

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

@task
def gpa_task(conn):
    etl_gpa.run_etl(conn)

@task
def enrollment_task(conn):
    etl_enrollment.run_etl(conn)

@task 
def comments_task(conn):
    etl_transcript_comments.run_etl(conn)

@task
def parents_task():
    conn = pg_connect()
    try:
        etl_parents.run_etl(conn)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

@task
def mailsync_task():
    exe_path = r"C:\Users\Install\mailsync\blackbaud-mailsync.exe"
    exe_dir = os.path.dirname(exe_path)

    try:
        result = subprocess.run(
            f'"{exe_path}"',
            shell=True,
            cwd=exe_dir,  # Ensures the .env file is discoverable
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if result.returncode != 0:
            print("MailSync failed:", result.stderr.decode("utf-8", errors="replace"))
        else:
            print("MailSync completed successfully")
    except Exception as e:
        print(f"Error launching MailSync: {e}")

@flow(task_runner=SequentialTaskRunner())
def run_mailsync():
    parents_task()
    mailsync_task()

@flow
def run_attendance():
    try:
        conn = pg_connect()
        etl_attendance.run_etl(conn)
        conn.commit()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print("error in transaction, reverting")
        conn.rollback()

@flow
def run_transcripts():
    try:
        conn = pg_connect()
        conn.autocommit = False

        enrollment_task(conn)
        transcripts_task(conn)
        gpa_task(conn)
        comments_task(conn)

        conn.commit()
        conn.close()
        
    except (Exception, psycopg2.DatabaseError) as error:
        # Exception catches all errors so psycopg2.DatabaseError is not necessary
        print("error in transaction, reverting")
        conn.rollback()

  
if __name__ == "__main__":
    attendance_deploy = run_attendance.to_deployment(name="run_attendance",
    interval=86400)
    transcripts_deploy = run_transcripts.to_deployment(name="run_transcripts",
	interval=86400)
    mailsync_deploy = run_mailsync.to_deployment(name="run_mailsync",
	interval=86400)
    serve(attendance_deploy, transcripts_deploy, mailsync_deploy)
