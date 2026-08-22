import os
from datetime import datetime

from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
REVIEW_ACTION_DESK_ID = os.getenv("REVIEW_ACTION_DESK_ID")
SYSTEM_RUN_LOG_ID = os.getenv("SYSTEM_RUN_LOG_ID")

notion = Client(auth=NOTION_TOKEN)


def create_review_request(roll_no, status="Pending"):
    response = notion.pages.create(
        parent={
            "database_id": REVIEW_ACTION_DESK_ID
        },
        properties={
            "Request": {
                "title": [
                    {
                        "text": {
                            "content": f"Attendance Warning - {roll_no}"
                        }
                    }
                ]
            },
            "Roll No": {
                "rich_text": [
                    {
                        "text": {
                            "content": str(roll_no)
                        }
                    }
                ]
            },
            "Status": {
                "select": {
                    "name": status
                }
            }
        }
    )

    return response


def create_run_log(event):
    response = notion.pages.create(
        parent={
            "database_id": SYSTEM_RUN_LOG_ID
        },
        properties={
            "Run Event": {
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