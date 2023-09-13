from BbApiConnector import BbApiConnector
import os

print('hello world')

#path = os.path.join(os.pardir, r'\config\app_secrets.json')
path = r'C:\Users\Michael.Lindner\Documents\BlackbaudExtractor\config\app_secrets.json'

api_conn = BbApiConnector(path)
bb_session = api_conn.get_session()

# todo: put in functions, add docstring

# Get attendance data
# https://api.sky.blackbaud.com/school/v1/attendance?level_id={level_id}&day={day}&offering_type={offering_type}[&excuse_type]
# level_id, required, integer	
# The ID of the school level to retrieve attendance records.

# day, required, string
#The date to return attendance for.

# offering_type, required, integer
# The offering type to retrieve records for.

# excuse_type, optional, integer
# Filters results to a specific excuse type.

# returns
#{
#  "type": "object",
#  "properties": {
#    "count": {
#      "type": "integer",
#      "description": "The number of items in the collection",
#      "format": "int32",
#      "readOnly": true
#    },
#    "next_link": {
#      "type": "string",
#      "description": "For paginated responses, the URI for the next page of results",
#      "nullable": true
#    },
#    "value": {
#      "type": "array",
#      "items": {
#        "type": "object",
#        "properties": {
#          "id": {
#            "type": "integer",
#            "description": "The ID of the attendance",
#            "format": "int64"
#          },
#          "attendance_of_record": {
#            "type": "boolean",
#            "description": "Attendance of record"
#          },
#          "attendance_type": {
#            "type": "boolean",
#            "description": "The type of the attendance"
#          },
#          "block_name": {
#            "type": "string",
#            "description": "The name of the block",
#            "nullable": true
#          },
#          "comment": {
#            "type": "string",
#            "description": "Attendance record comment",
#            "nullable": true
#          },
#          "date": {
#            "type": "string",
#            "description": "The date of the attendance record. Uses <a href=\"https://tools.ietf.org/html/rfc3339\" target=\"_blank\">ISO-8601</a> (24H) format: 2003-04-21T10:29:43",
#            "format": "date-time",
#            "nullable": true
#          },
#          "excuse_category_description": {
#            "type": "string",
#            "description": "The category description of the excuse",
#            "nullable": true
#          },
#          "excuse_category_id": {
#            "type": "integer",
#            "description": "The category of the excuse",
#            "format": "int32"
#          },
#          "excuse_description": {
#            "type": "string",
#            "description": "The description of the excuse",
#            "nullable": true
#          },
#          "excuse_type_id": {
#            "type": "integer",
#            "description": "The type of the excuse",
#            "format": "int32"
#          },
#          "excused": {
#            "type": "integer",
#            "description": "Whether the absence was excused",
#            "format": "int32"
#          },
#          "grad_year": {
#            "type": "string",
#            "description": "The graduation year of the student",
#            "nullable": true
#          },
#          "grade": {
#            "type": "string",
#            "description": "The grade of the student",
#            "nullable": true
#          },
#          "grade_level_sort": {
#            "type": "integer",
#            "description": "Grade level sort order",
#            "format": "int32"
#          },
#          "group_name": {
#            "type": "string",
#            "description": "The group name",
#            "nullable": true
#          },
#          "photo_file_name": {
#            "type": "string",
#            "description": "The phone file name",
#            "nullable": true
#          },
#          "section": {
#            "type": "string",
#            "description": "The section",
#            "nullable": true
#          },
#          "section_id": {
#            "type": "integer",
#            "description": "The ID of the section",
#            "format": "int32"
#          },
#          "student_name": {
#            "type": "string",
#            "description": "The name of the student",
#            "nullable": true
#          },
#          "student_user_id": {                                               PRIMARY KEY
#            "type": "integer",
#            "description": "The student user ID",
#            "format": "int32"
#          },
#          "teacher_name": {
#            "type": "string",
#            "description": "The name of the teacher",
#            "nullable": true
#          }
#        },
#        "additionalProperties": false,
#        "description": "Attendance Model"
#      },
#      "description": "The set of items included in the response. This may be a subset of the items in the collection",
#      "nullable": true
#    }
#  },
#  "additionalProperties": false,
#  "description": "A Collection"
#}
params = {
    'level_id': 779,
    'day': '3/14/2022',
    'offering_type': 1
 }
req = bb_session.get("https://api.sky.blackbaud.com/school/v1/attendance", params=params)

print(req.json()['value'][0])
output = req.json()['value']

for i in range(len(output)):
    print(output[i]['student_user_id'])



