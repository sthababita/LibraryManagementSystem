from django.core.mail import send_mail
from django.core.mail import BadHeaderError
from django.conf import settings
import logging
import smtplib


logger = logging.getLogger(__name__)


def send_simple_email(subject: str, message: str, recipient_list: list):
    """
    Sends a simple email using Django's email system.

    Args:
        subject (str): Email subject
        message (str): Email body
        recipient_list (list): List of recipient emails
    """
    if not recipient_list:
        return False

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False
        )
    except (BadHeaderError, smtplib.SMTPException, OSError) as exc:
        logger.warning("Email delivery failed for %s: %s", recipient_list, exc)
        return False

    return True


def send_student_deadline_email(student_name: str, course_name: str, deadline, recipient_list: list):
    """
    Sends a personalized email to students about assignment/course deadlines.

    Args:
        student_name (str): Name of the student
        course_name (str): Name of the course
        deadline (datetime or str): Assignment/course deadline
        recipient_list (list): List of recipient emails
    """
    if hasattr(deadline, "strftime"):
        deadline_str = deadline.strftime('%Y-%m-%d %H:%M')
    else:
        deadline_str = str(deadline)

    subject = f"Assignment Deadline Reminder - {course_name}"
    message = (
        f"Dear {student_name},\n\n"
        f"This is a reminder that your assignment for the course '{course_name}' "
        f"is due on {deadline_str}.\n\n"
        f"Please make sure to submit it on time.\n\n"
        f"Best regards,\nELMS Team"
    )

    return send_simple_email(subject, message, recipient_list)


def send_sponsor_progress_email(sponsor_name: str, student_name: str, progress: float, recipient_list: list):
    """
    Sends a personalized email to sponsors about the progress of their sponsored student.

    Args:
        sponsor_name (str): Name of the sponsor
        student_name (str): Name of the student
        progress (float/int): Student progress percentage
        recipient_list (list): List of recipient emails
    """
    subject = f"Progress Update - {student_name}"
    message = (
        f"Dear {sponsor_name},\n\n"
        f"We are pleased to share the latest progress of your sponsored student, {student_name}.\n"
        f"Current Progress: {progress}%\n\n"
        f"Thank you for your continued support.\n\n"
        f"Best regards,\nELMS Team"
    )

    return send_simple_email(subject, message, recipient_list)


def send_instructor_progress_email(student_name: str, instructor_name: str, progress: float, recipient_list: list):
    """
    Sends a progress update email to the course instructor about a student's progress.

    Args:
        student_name (str): Name of the student
        instructor_name (str): Name of the instructor
        progress (float/int): Student progress percentage
        recipient_list (list): List of recipient emails
    """
    subject = f"Progress Update - {student_name}"
    message = (
        f"Dear {instructor_name},\n\n"
        f"Student '{student_name}' has completed {progress}% of the course.\n\n"
        f"Best regards,\nELMS Team"
    )

    return send_simple_email(subject, message, recipient_list)
