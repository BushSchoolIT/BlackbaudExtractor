import os
import sys
import io
import subprocess
import postgres_credentials
import psycopg2
import etl_attendance
import etl_transcripts
import etl_gpa
import etl_enrollment
import etl_transcript_comments
import etl_parents

# SETUP environment BEFORE importing prefect (important)
os.environ["PREFECT_API_URL"] = "http://localhost:4200/api"
WORK_POOL = "work_pool_0"

from prefect import flow, serve, task
from prefect.task_runners import SequentialTaskRunner
from prefect.deployments import Deployment

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
def transcripts_task_py(conn):
    etl_transcripts.run_etl(conn)

@task
def gpa_task_py(conn):
    etl_gpa.run_etl(conn)

@task
def enrollment_task_py(conn):
    etl_enrollment.run_etl(conn)

@task 
def comments_task_py(conn):
    etl_transcript_comments.run_etl(conn)

@task
def parents_task_py():
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
def mailsync_task_py():
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
def run_mailsync_py():
    parents_task_py()
    mailsync_task_py()

@flow
def run_attendance_py():
    try:
        conn = pg_connect()
        etl_attendance.run_etl(conn)
        conn.commit()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print("error in transaction, reverting")
        conn.rollback()

@flow
def run_transcripts_py():
    try:
        conn = pg_connect()
        conn.autocommit = False

        enrollment_task_py(conn)
        transcripts_task_py(conn)
        gpa_task_py(conn)
        comments_task_py(conn)

        conn.commit()
        conn.close()
        
    except (Exception, psycopg2.DatabaseError) as error:
        # Exception catches all errors so psycopg2.DatabaseError is not necessary
        print("error in transaction, reverting")
        conn.rollback()

  
if __name__ == "__main__":
    Deployment.build_from_flow(
        flow=run_attendance_py,
        name="run_attendance_py",
        work_pool_name=WORK_POOL,
        schedule={"interval": 86400}
    ).apply()

    Deployment.build_from_flow(
        flow=run_transcripts_py,
        name="run_transcripts_py",
        work_pool_name=WORK_POOL,
        schedule={"interval": 86400}
    ).apply()

    Deployment.build_from_flow(
        flow=run_mailsync_py,
        name="run_mailsync_py",
        work_pool_name=WORK_POOL,
        schedule={"interval": 86400}
    ).apply()
