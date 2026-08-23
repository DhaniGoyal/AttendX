import os
from datetime import datetime

from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
REVIEW_ACTION_DESK_ID = os.getenv("REVIEW_ACTION_DESK_ID")
SYSTEM_RUN_LOG_ID = os.getenv("SYSTEM_RUN_LOG_ID")

notion = Client(auth=NOTION_TOKEN)


def create_review_request(
    roll_no,
    student_name,
    issue_type,
    attendance_percentage=None,
    rule_reason="",
    request_id=None,
    status="Pending"
):

    properties = {
        "Request": {
            "title": [
                {
                    "text": {
                        "content": f"Attendance Review - {roll_no}"
                    }
                }
            ]
        },

        "Roll No": {
            "number": int(roll_no)
        },

        "Student Name": {
            "rich_text": [
                {
                    "text": {
                        "content": student_name
                    }
                }
            ]
        },

        "Issue Type": {
            "select": {
                "name": issue_type
            }
        },

        "Attendance %": {
            "number": (
                float(attendance_percentage)
                if attendance_percentage is not None
                else 0
            )
        },

        "Rule Reason": {
            "rich_text": [
                {
                    "text": {
                        "content": rule_reason
                    }
                }
            ]
        },

        "Status": {
            "select": {
                "name": status
            }
        },

        "Professor Decision": {
            "select": {
                "name": "Pending"
            }
        }
    }

    if request_id is not None:
        properties["Warning Request ID"] = {
            "number": int(request_id)
        }

    response = notion.pages.create(
        parent={
            "database_id": REVIEW_ACTION_DESK_ID
        },
        properties=properties
    )

    return response
def create_run_log(event):

    response = notion.pages.create(
        parent={
            "database_id": SYSTEM_RUN_LOG_ID
        },
        properties={
            "Run / Event": {
                "title": [
                    {
                        "text": {
                            "content": event
                        }
                    }
                ]
            },

            "Timestamp": {
                "date": {
                    "start": datetime.now().isoformat()
                }
            }
        }
    )

    return response


def get_approved_requests():

    database = notion.databases.retrieve(
        database_id=REVIEW_ACTION_DESK_ID
    )

    data_source_id = database["data_sources"][0]["id"]

    response = notion.data_sources.query(
        data_source_id=data_source_id,
        filter={
            "property": "Professor Decision",
            "select": {
                "equals": "Approve"
            }
        }
    )

    return response["results"]







def get_professor_decision_requests():

    database = notion.databases.retrieve(
        database_id=REVIEW_ACTION_DESK_ID
    )

    data_source_id = database["data_sources"][0]["id"]

    response = notion.data_sources.query(
        data_source_id=data_source_id,
        filter={
            "or": [
                {
                    "property": "Professor Decision",
                    "select": {
                        "equals": "Approve"
                    }
                },
                {
                    "property": "Professor Decision",
                    "select": {
                        "equals": "reject"
                    }
                },
                {
                    "property": "Professor Decision",
                    "select": {
                        "equals": "Ovverride"
                    }
                }
            ]
        }
    )

    return response["results"]






def get_page_roll_no(page):

    properties = page.get("properties", {})

    roll_property = properties.get("Roll No", {})

    if roll_property.get("type") == "number":
        return roll_property.get("number")

    return None


def get_page_issue_type(page):

    properties = page.get("properties", {})

    issue_property = properties.get("Issue Type", {})

    if issue_property.get("type") == "select":
        select_value = issue_property.get("select")

        if select_value:
            return select_value.get("name")

    return None





def update_request_status(page_id, status="Dispatched"):

    response = notion.pages.update(
        page_id=page_id,
        properties={
            "Status": {
                "select": {
                    "name": status
                }
            }
        }
    )

    return response





def get_professor_decision(page):

    properties = page.get("properties", {})

    decision_property = properties.get(
        "Professor Decision", {}
    )

    if decision_property.get("type") == "select":

        select_value = decision_property.get("select")

        if select_value:
            return select_value.get("name")

    return None