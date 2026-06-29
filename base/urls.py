from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AssignmentViewSet,
    CourseViewSet,
    EnrollmentViewSet,
    LoginView,
    NotificationViewSet,
    RegisterStudentView,
    SponsorshipViewSet,
    admin_dashboard_list,
    make_payment,
    notify_sponsors_progress,
    notify_students_deadline,
    send_email_api,
    sponsor_dashboard,
    sponsor_khalti_init,
    sponsor_khalti_verify,
)


router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")
router.register(r"assignments", AssignmentViewSet, basename="assignment")
router.register(r"sponsorships", SponsorshipViewSet, basename="sponsorship")
router.register(r"notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("", include(router.urls)),
    path("register/student/", RegisterStudentView.as_view(), name="register-student"),
    path("login/", LoginView.as_view(), name="login"),
    path("admin/dashboard/", admin_dashboard_list, name="admin-dashboard"),
    path("sponsor/dashboard/", sponsor_dashboard, name="sponsor-dashboard"),
    path("notify/students/", notify_students_deadline, name="notify-students"),
    path("notify/sponsors/", notify_sponsors_progress, name="notify-sponsors"),
    path("make-payment/", make_payment),
    path("email/send/", send_email_api),
    path("payment/sponsor/init/", sponsor_khalti_init),
    path("payment/sponsor/verify/", sponsor_khalti_verify),
]
