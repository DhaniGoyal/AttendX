from .notion_integration import (
    create_review_request,
    create_run_log,
    get_approved_requests,
    get_professor_decision_requests,
    get_page_roll_no,
    get_professor_decision
)


from .face_verification import compare_faces
from fastapi import FastAPI
from .database import engine, Base
from .models import Student, AttendanceRecord, WarningRequest
from .database import SessionLocal
from .pdf_generator import generate_warning_pdf
from .email_sender import send_email


Base.metadata.create_all(bind=engine)

app = FastAPI(title="AttendX")

@app.get("/")
def home():
    return {
        "project": "AttendX",
        "status": "Backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/check-in/{roll_no}")
def check_in(roll_no: str):
    db = SessionLocal()

    student = db.query(Student).filter(Student.roll_no == roll_no).first()

    if not student:
        db.close()
        return {
            "error": "Student not found"
        }

    student.total_classes += 1
    student.attended += 1

    record = AttendanceRecord(
        roll_no=student.roll_no,
        status="Present"
    )

    db.add(record)
    db.commit()

    attendance = (student.attended / student.total_classes) * 100

    db.close()

    return {
        "message": "Attendance marked successfully",
        "roll_no": student.roll_no,
        "name": student.name,
        "total_classes": student.total_classes,
        "attended": student.attended,
        "attendance_percentage": attendance
    }




@app.post("/students")
def create_student(
    roll_no: str,
    name: str,
    parent_phone: str
):
    db = SessionLocal()

    student = Student(
        roll_no=roll_no,
        name=name,
        parent_phone=parent_phone
    )

    db.add(student)
    db.commit()
    db.refresh(student)
    db.close()

    return {
        "message": "Student created successfully",
        "student_id": student.id,
        "roll_no": student.roll_no,
        "name": student.name
    }




@app.get("/students/{roll_no}")
def get_student(roll_no: str):
    db = SessionLocal()

    student = db.query(Student).filter(Student.roll_no == roll_no).first()

    if not student:
        db.close()
        return {
            "error": "Student not found"
        }

    attendance = 0

    if student.total_classes > 0:
        attendance = (student.attended / student.total_classes) * 100

    db.close()

    return {
        "roll_no": student.roll_no,
        "name": student.name,
        "total_classes": student.total_classes,
        "attended": student.attended,
        "attendance_percentage": attendance
    }

@app.get("/students/{roll_no}/status")
def student_status(roll_no: str):
    db = SessionLocal()

    student = db.query(Student).filter(Student.roll_no == roll_no).first()

    if not student:
        db.close()
        return {
            "error": "Student not found"
        }

    if student.total_classes == 0:
        attendance = 0
    else:
        attendance = (student.attended / student.total_classes) * 100

    if attendance < 75:
        status = "Defaulter"
        warning_required = True
    else:
        status = "Safe"
        warning_required = False

    db.close()

    return {
        "roll_no": student.roll_no,
        "name": student.name,
        "attendance_percentage": attendance,
        "status": status,
        "warning_required": warning_required
    }


@app.post("/absent/{roll_no}")
def mark_absent(roll_no: str):
    db = SessionLocal()

    student = db.query(Student).filter(Student.roll_no == roll_no).first()

    if not student:
        db.close()
        return {
            "error": "Student not found"
        }

    student.total_classes += 1

    record = AttendanceRecord(
        roll_no=student.roll_no,
        status="Absent"
    )

    db.add(record)
    db.commit()

    if student.total_classes > 0:
        attendance = (student.attended / student.total_classes) * 100
    else:
        attendance = 0

    if attendance < 75:
        pdf_path = generate_warning_pdf(
            student.name,
            student.roll_no,
            student.total_classes,
            student.attended,
            attendance
        )

        send_email(
            to_email="vaanigoel15@gmail.com",
            subject="AttendX Attendance Warning",
            body=f"""
Dear Student,

Your attendance is below the required minimum of 75%.

Student Name: {student.name}
Roll Number: {student.roll_no}
Attendance: {attendance:.2f}%

Please maintain regular attendance.

Regards,
AttendX
""",
            pdf_path=pdf_path
        )

    db.close()

    return {
        "message": "Absence marked successfully",
        "roll_no": student.roll_no,
        "name": student.name,
        "total_classes": student.total_classes,
        "attended": student.attended,
        "attendance_percentage": attendance
    }


@app.get("/students/{roll_no}/attendance-history")
def attendance_history(roll_no: str):
    db = SessionLocal()

    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.roll_no == roll_no
    ).all()

    db.close()

    return {
        "roll_no": roll_no,
        "total_records": len(records),
        "attendance_history": [
            {
                "status": record.status
            }
            for record in records
        ]
    }





@app.get("/defaulters")
def get_defaulters():
    db = SessionLocal()

    students = db.query(Student).all()

    defaulters = []

    for student in students:
        if student.total_classes == 0:
            continue

        attendance = (student.attended / student.total_classes) * 100

        if attendance < 75:
            defaulters.append({
                "roll_no": student.roll_no,
                "name": student.name,
                "attendance_percentage": attendance,
                "warning_required": True
            })

    db.close()

    return {
        "total_defaulters": len(defaulters),
        "defaulters": defaulters
    }





@app.get("/students/{roll_no}/warning-pdf")
def warning_pdf(roll_no: str):
    db = SessionLocal()

    student = db.query(Student).filter(Student.roll_no == roll_no).first()

    if not student:
        db.close()
        return {
            "error": "Student not found"
        }

    if student.total_classes == 0:
        db.close()
        return {
            "error": "No attendance records found"
        }

    attendance = (student.attended / student.total_classes) * 100

    if attendance >= 75:
        db.close()
        return {
            "message": "Student is not a defaulter",
            "attendance_percentage": attendance
        }

    pdf_path = generate_warning_pdf(
        student.name,
        student.roll_no,
        student.total_classes,
        student.attended,
        attendance
    )
    send_email(
    to_email="vaanigoel15@gmail.com",
    subject="AttendX Attendance Warning",
    body=f"""
Dear Student,

Your attendance is below the required minimum of 75%.

Student Name: {student.name}
Roll Number: {student.roll_no}
Attendance: {attendance:.2f}%

Please maintain regular attendance.

Regards,
AttendX
""",
    pdf_path=pdf_path
)

    db.close()

    return {
        "message": "Warning PDF generated successfully",
        "roll_no": student.roll_no,
        "attendance_percentage": attendance,
        "pdf_path": pdf_path
    }


@app.post("/verify-check-in/{roll_no}")
def verify_check_in(roll_no: str):

    result = compare_faces(
        "baseline.jpg",
        "live.jpg"
    )

    if not result["success"]:
        return {
            "roll_no": roll_no,
            "message": result["message"]
        }

    # Face match nahi hua → Proxy request create
    if result["status"] != "Present":

        db = SessionLocal()

        try:
            student = db.query(Student).filter(
                Student.roll_no == roll_no
            ).first()

            if not student:
                return {
                    "error": "Student not found"
                }

            create_review_request(
                roll_no=student.roll_no,
                student_name=student.name,
                issue_type="Proxy Flag",
                rule_reason="Face verification failed. Proxy suspected.",
                status="Pending"
            )

            create_run_log(
                f"Proxy suspected - Roll No {student.roll_no}"
            )

            return {
                "roll_no": roll_no,
                "name": student.name,
                "similarity": float(result["similarity"]),
                "status": "Proxy Suspected",
                "message": "Face verification failed. Proxy request sent for review."
            }

        finally:
            db.close()

    # Student database se find karo
    db = SessionLocal()

    student = db.query(Student).filter(
        Student.roll_no == roll_no
    ).first()

    if not student:
        db.close()
        return {
            "error": "Student not found"
        }

    # Face match hua → attendance mark
    student.total_classes += 1
    student.attended += 1

    record = AttendanceRecord(
        roll_no=student.roll_no,
        status="Present"
    )

    db.add(record)
    db.commit()

    attendance = (
        student.attended /
        student.total_classes
    ) * 100

    db.close()

    return {
        "message": "Face verified. Attendance marked successfully",
        "roll_no": student.roll_no,
        "name": student.name,
        "similarity": float(result["similarity"]),
        "status": "Present",
        "total_classes": student.total_classes,
        "attended": student.attended,
        "attendance_percentage": attendance
    }





@app.post("/leave-request/{roll_no}")
def create_leave_request(roll_no: str):
    db = SessionLocal()

    try:
        student = db.query(Student).filter(
            Student.roll_no == roll_no
        ).first()

        if not student:
            return {
                "error": "Student not found"
            }

        attendance = 0

        if student.total_classes > 0:
            attendance = (
                student.attended / student.total_classes
            ) * 100

        create_review_request(
            roll_no=student.roll_no,
            student_name=student.name,
            issue_type="Leave Request",
            attendance_percentage=attendance,
            rule_reason="Student submitted a leave request",
            status="Pending"
        )

        create_run_log(
            f"Leave request created - Roll No {student.roll_no}"
        )

        return {
            "message": "Leave request created",
            "roll_no": student.roll_no,
            "name": student.name,
            "attendance_percentage": attendance,
            "issue_type": "Leave Request",
            "status": "Pending"
        }

    except Exception as e:
        db.rollback()
        return {
            "error": str(e),
            "error_type": type(e).__name__
        }

    finally:
        db.close()




@app.post("/warning-request/{roll_no}")
def create_warning_request(roll_no: str):
    db = SessionLocal()

    try:
        student = db.query(Student).filter(
            Student.roll_no == roll_no
        ).first()

        if not student:
            return {"error": "Student not found"}

        if student.total_classes == 0:
            return {"error": "No attendance records found"}

        attendance = (student.attended / student.total_classes) * 100

        if attendance >= 75:
            return {
                "message": "Student is not a defaulter",
                "attendance_percentage": attendance
            }

        # Check if an active warning already exists
        existing_request = db.query(WarningRequest).filter(
            WarningRequest.roll_no == student.roll_no,
            WarningRequest.dispatched == 0
        ).first()

        if existing_request:
            return {
                "message": "Warning request already exists",
                "request_id": existing_request.id,
                "roll_no": student.roll_no,
                "attendance_percentage": attendance,
                "status": existing_request.status
            }

        # Create new warning request
        request = WarningRequest(
            roll_no=student.roll_no,
            status="Pending"
        )

        db.add(request)
        db.commit()
        db.refresh(request)

        create_review_request(
            roll_no=student.roll_no,
            student_name=student.name,
            issue_type="Defaulter",
            attendance_percentage=attendance,
            rule_reason="Attendance below 75%",
            request_id=request.id,
            status="Pending"
        )

        create_run_log(
            f"Warning request created - Roll No {student.roll_no}"
        )

        return {
            "message": "Warning request created",
            "request_id": request.id,
            "roll_no": student.roll_no,
            "attendance_percentage": attendance,
            "status": "Pending"
        }

    except Exception as e:
        db.rollback()
        return {
            "error": str(e)
        }

    finally:
        db.close()


@app.post("/warning-request/{request_id}/approve")
def approve_warning(request_id: int):
    db = SessionLocal()

    try:
        request = db.query(WarningRequest).filter(
            WarningRequest.id == request_id
        ).first()

        if not request:
            return {"error": "Warning request not found"}

        if request.status == "Approved":
            return {"message": "Warning already approved"}

        student = db.query(Student).filter(
            Student.roll_no == request.roll_no
        ).first()

        if not student:
            return {"error": "Student not found"}

        attendance = (
            student.attended / student.total_classes
        ) * 100

        pdf_path = generate_warning_pdf(
            student.name,
            student.roll_no,
            student.total_classes,
            student.attended,
            attendance
        )

        send_email(
            to_email="vaanigoel15@gmail.com",
            subject="AttendX Attendance Warning",
            body=f"""
Dear Student,

Your attendance is below the required minimum of 75%.

Student Name: {student.name}
Roll Number: {student.roll_no}
Attendance: {attendance:.2f}%

Please maintain regular attendance.

Regards,
AttendX
""",
            pdf_path=pdf_path
        )

        request.status = "Approved"
        db.commit()

        create_run_log(
            f"Warning approved and dispatched - Roll No {student.roll_no}"
        )

        return {
            "message": "Warning approved and dispatched",
            "roll_no": student.roll_no,
            "attendance_percentage": attendance,
            "status": "Approved",
            "pdf_path": pdf_path
        }

    except Exception as e:
        db.rollback()
        return {
            "error": str(e),
            "error_type": type(e).__name__
        }

    finally:
        db.close()


@app.get("/notion-approved")
def notion_approved():
    try:
        requests = get_approved_requests()

        return {
            "approved_count": len(requests),
            "approved_requests": requests
        }

    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__
        }




@app.post("/process-notion-approvals")
def process_notion_approvals():
    db = SessionLocal()
    processed = []

    try:
        approved_requests = get_professor_decision_requests()

        for page in approved_requests:

            roll_no = get_page_roll_no(page)
            issue_type = get_page_issue_type(page)

            if roll_no is None or issue_type is None:
                continue

            decision = get_professor_decision(page)

            if decision is None or decision == "Pending":
                continue


            # -----------------------------
            # REJECT
            # -----------------------------
            if decision == "reject":

                update_request_status(
                    page["id"],
                    "Rejected"
                )

                create_run_log(
                    f"Request rejected - Roll No {roll_no} - {issue_type}"
                )

                processed.append({
                    "roll_no": str(roll_no),
                    "issue_type": issue_type,
                    "status": "Rejected"
                })

                continue


            # -----------------------------
            # LEAVE REQUEST
            # -----------------------------
            if issue_type == "Leave Request":

                update_request_status(
                    page["id"],
                    "Approved"
                )

                create_run_log(
                    f"Leave request approved - Roll No {roll_no}"
                )

                processed.append({
                    "roll_no": str(roll_no),
                    "issue_type": "Leave Request",
                    "status": "Approved"
                })

                continue


            # -----------------------------
            # PROXY FLAG
            # -----------------------------
            if issue_type == "Proxy Flag":

                update_request_status(
                    page["id"],
                    "Approved"
                )

                create_run_log(
                    f"Proxy flag approved - Roll No {roll_no}"
                )

                processed.append({
                    "roll_no": str(roll_no),
                    "issue_type": "Proxy Flag",
                    "status": "Approved"
                 })

                continue


            # -----------------------------
            # DEFAULTER / WARNING REQUEST
            # -----------------------------
            if issue_type == "Defaulter":

                request = db.query(WarningRequest).filter(
                    WarningRequest.roll_no == str(roll_no),
                    WarningRequest.status == "Pending",
                    WarningRequest.dispatched == 0
                ).first()

                if not request:
                    continue

                student = db.query(Student).filter(
                    Student.roll_no == str(roll_no)
                ).first()

                if not student:
                    continue

                if student.total_classes == 0:
                    continue

                attendance = (
                    student.attended / student.total_classes
                ) * 100

                pdf_path = generate_warning_pdf(
                    student.name,
                    student.roll_no,
                    student.total_classes,
                    student.attended,
                    attendance
                )

                send_email(
                    to_email="vaanigoel50@gmail.com",
                    subject="AttendX Attendance Warning",
                    body=f"""
Dear Student,

Your attendance is below the required minimum of 75%.

Student Name: {student.name}
Roll Number: {student.roll_no}
Attendance: {attendance:.2f}%

Please maintain regular attendance.

Regards,
AttendX
""",
                    pdf_path=pdf_path
                )

                request.status = "Approved"
                request.dispatched = 1

                db.commit()

                update_request_status(
                    page["id"],
                    "Dispatched"
                )

                create_run_log(
                    f"Automatic warning dispatched - Roll No {student.roll_no}"
                )

                processed.append({
                    "roll_no": student.roll_no,
                    "issue_type": "Defaulter",
                    "attendance_percentage": attendance,
                    "status": "Dispatched"
                })

        return {
            "processed_count": len(processed),
            "processed": processed
        }

    except Exception as e:
        db.rollback()

        return {
            "error": str(e),
            "error_type": type(e).__name__
        }

    finally:
        db.close()