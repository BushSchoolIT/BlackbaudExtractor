from prefect import flow
import etl_attendance
import etl_transcripts
import etl_gpa


@flow
def run_attendance():
	 
@flow
def run_transcripts():
	 
@flow
def run_gpa():
	 
   
  
if __name__ == "__main__":
    run_attendance.serve(name="run_attendance",
    interval=3600)