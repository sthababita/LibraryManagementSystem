from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response

# Create your views here.
from django.contrib.auth import authenticate, login

from django.contrib.auth.models import User,Group

from rest_framework import viewsets, permissions, filters,generics,serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.core.mail import send_mail
from .models import Course, Enrollment, Assignment, Sponsorship, Notification,Payment
from .serializers import AdminDashboardSerializer, CourseSerializer, EmailSendSerializer, EnrollmentSerializer, AssignmentSerializer, LoginSerializer, SponsorshipSerializer, NotificationSerializer,RegisterSerializer
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Avg
from base.utils import send_simple_email,send_student_deadline_email, send_sponsor_progress_email
from django.conf import settings
import requests

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .serializers import EmailSendSerializer
from .utils.email_utils import send_simple_email


# Pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

def check_group(user, group_name):
    return user.groups.filter(name=group_name).exists()
# Admin Dashboard
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from base.serializers import AdminDashboardSerializer
from django.contrib.auth.models import User
from base.models import Course, Enrollment

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.models import User
from base.models import Course, Enrollment
from base.serializers import AdminDashboardSerializer

#from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from base.models import Course, Enrollment
from django.contrib.auth.models import User
from base.serializers import AdminDashboardSerializer

@swagger_auto_schema(
    method='get',
    responses={200: AdminDashboardSerializer},
    operation_description="Admin dashboard summary. Returns total students, courses, and enrollments."
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_list(request):
    """
    Returns a summary of the system for Admin users:
    - total_students: Total number of users
    - total_courses: Total number of courses
    - total_enrollments: Total number of enrollments
    """
    # Check if user is in Admin group
    if not check_group(request.user, 'Admin'):
        return Response(
            {'error': 'You do not have permission for this dashboard.'},
            status=403
        )

    # Prepare dashboard data
    data = {
        "total_students": User.objects.count(),
        "total_courses": Course.objects.count(),
        "total_enrollments": Enrollment.objects.count()
    }

    # Serialize and return
    serializer = AdminDashboardSerializer(data)
    return Response(serializer.data)


# Sponsor Dashboard
'''@api_view(['GET'])
@permission_classes([IsAuthenticated])

def sponsor_dashboard(request):
    if not check_group(request.user, 'Sponsor'):
        return Response({'error': 'You do not have permission for this dashboard.'}, status=403)
    
    total_sponsored_funds = Sponsorship.objects.aggregate(total_funds=Sum('amount'))['total_funds'] or 0
    total_used_funds = 0  # Remove used_amount since model doesn't have it

    students_sponsored = User.objects.filter(sponsorship__isnull=False).distinct().count()
    enrollments = Enrollment.objects.filter(student__sponsorship__isnull=False)
    avg_progress = enrollments.aggregate(avg_progress=Avg('progress'))['avg_progress'] if enrollments.exists() else 0

    fund_utilization_percent = (total_used_funds / total_sponsored_funds * 100) if total_sponsored_funds > 0 else 0

    data = {
        "total_sponsored_funds": total_sponsored_funds,
        "total_used_funds": total_used_funds,
        "fund_utilization_percent": fund_utilization_percent,
        "students_sponsored": students_sponsored,
        "average_student_progress": avg_progress
    }

    return Response(data)'''

from django.db.models import Sum, Avg

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sponsor_dashboard(request):
    if not check_group(request.user, 'Sponsor'):
        return Response({'error': 'You do not have permission for this dashboard.'}, status=403)
    
    # Total funds from Sponsorships
    total_sponsored_funds = Sponsorship.objects.aggregate(total_funds=Sum('amount'))['total_funds'] or 0
    total_used_funds = 0  # keep 0 for now since you don't track used_amount

    # Students sponsored (using the correct related name)
    students_sponsored = User.objects.filter(sponsored_students__isnull=False).distinct().count()
    
    # Enrollments of sponsored students
    enrollments = Enrollment.objects.filter(student__sponsored_students__isnull=False)
    avg_progress = enrollments.aggregate(avg_progress=Avg('progress'))['avg_progress'] if enrollments.exists() else 0

    fund_utilization_percent = (total_used_funds / total_sponsored_funds * 100) if total_sponsored_funds > 0 else 0

    data = {
        "total_sponsored_funds": total_sponsored_funds,
        "total_used_funds": total_used_funds,
        "fund_utilization_percent": fund_utilization_percent,
        "students_sponsored": students_sponsored,
        "average_student_progress": avg_progress
    }

    return Response(data)



# Registration Serializer
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


# Registration View
class RegisterStudentView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        student_group, created = Group.objects.get_or_create(name='Student')
        user.groups.add(student_group)


# Login View (class-based)
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response({
            "message": "Login successful",
            "username": user.username,
        })






from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    queryset = Course.objects.none()  # ✅ safer

    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'instructor__username']
    filterset_fields = ['difficulty']

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.groups.filter(name='Admin').exists():
            return Course.objects.all()

        if user.groups.filter(name='Instructor').exists():
            return Course.objects.filter(instructor=user)

        if user.groups.filter(name='student').exists():
            return Course.objects.all()

        return Course.objects.none()



# Enrollments
class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Student').exists():
            return Enrollment.objects.filter(student=user)
        elif user.groups.filter(name='Instructor').exists():
            return Enrollment.objects.filter(course__instructor=user)
        return Enrollment.objects.none()

# Assessments
class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

# Sponsorships
class SponsorshipViewSet(viewsets.ModelViewSet):
    queryset = Sponsorship.objects.all()
    serializer_class = SponsorshipSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['student__username','sponsor__username']
    filterset_fields = ['status']

# Notifications
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


# Example: Sending notification emails
def send_course_deadline_email(student_email, course_name):
    send_mail(
        subject=f'Course Deadline: {course_name}',
        message=f'Dear Student, your course "{course_name}" deadline is approaching!',
        from_email='no-reply@lms.com',
        recipient_list=[student_email],
        fail_silently=False
    )






from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Enrollment
from .utils import (
    send_student_deadline_email,
    send_sponsor_progress_email
)

@api_view(['POST'])
def notify_students_deadline(request):
    enrollments = Enrollment.objects.all()
    for e in enrollments:
        send_student_deadline_email(
            e.student.email,
            e.course.name,
            "2026-02-01"
        )
    return Response({"message": "Student deadline emails sent"})

@api_view(['POST'])
def notify_sponsors_progress(request):
    for e in Enrollment.objects.all():
        if hasattr(e.student, 'sponsored_students'):
            sponsor = e.student.sponsored_students.first().sponsor
            send_sponsor_progress_email(
                sponsor.email,
                e.student.username,
                e.progress
            )
    return Response({"message": "Sponsor progress emails sent"})


from .models import Payment
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
def make_payment(request):
    Payment.objects.create(
        sponsor=request.user,
        student_id=request.data['student_id'],
        amount=request.data['amount']
    )
    return Response({"message": "Payment successful"})







@swagger_auto_schema(
    method='post',
    request_body=EmailSendSerializer,
    responses={201: "Email sent successfully", 400: "Invalid data"}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_email_api(request):
    serializer = EmailSendSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        send_simple_email(
            subject=data['subject'],
            message=data['message'],
            recipient_list=data['recipients']
        )
        return Response({"message": "Email sent successfully"}, status=201)
    return Response(serializer.errors, status=400)




from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Enrollment
from base.utils.email_utils import send_student_deadline_email

@api_view(['POST'])
def notify_students_deadline(request):
    """
    Notify students about upcoming course deadlines.
    Sends one email per student per course.
    """
    enrollments = Enrollment.objects.all()

    # Use a set to avoid sending duplicate emails to the same student for the same course
    sent = set()

    for e in enrollments:
        key = (e.student.email, e.course.name)
        if key not in sent:
            sent.add(key)
            
            # Pull deadline dynamically from the model if available, else fallback
            deadline = getattr(e.course, 'deadline', '2026-02-01')  # replace with your field

            send_student_deadline_email(
                course_name=e.course.name,
                deadline=deadline,
                recipient_list=[e.student.email]  # must be a list
            )

    return Response({"message": "Student deadline emails sent successfully"})




from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Enrollment
from base.utils.email_utils import send_sponsor_progress_email

@api_view(['POST'])
def notify_sponsors_progress(request):
    """
    Notify sponsors about the progress of their sponsored students.
    Sends one email per sponsor per student.
    """
    enrollments = Enrollment.objects.all()
    sent = set()

    for e in enrollments:
        if hasattr(e.student, 'sponsored_students') and e.student.sponsored_students.exists():
            sponsor = e.student.sponsored_students.first().sponsor
            key = (sponsor.email, e.student.username)
            
            if key not in sent:
                sent.add(key)

                send_sponsor_progress_email(
                    student_name=e.student.username,
                    progress=e.progress,
                    recipient_list=[sponsor.email]  # must be a list
                )

    return Response({"message": "Sponsor progress emails sent successfully"})




# ------------------------------
# Swagger Schema for INIT API
# ------------------------------
sponsor_payment_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["student_id", "course_id", "amount"],
    properties={
        "student_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the student being sponsored"),
        "course_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the course"),
        "amount": openapi.Schema(type=openapi.TYPE_NUMBER, description="Amount in NPR")
    }
)

# ------------------------------
# INIT API: Create sponsorship & get Khalti payment URL
# ------------------------------
@swagger_auto_schema(
    method="post",
    request_body=sponsor_payment_schema,
    responses={
        200: openapi.Response(
            description="Khalti payment URL",
            examples={
                "application/json": {
                    "payment_url": "https://khalti.com/payment/checkout/pidx=..."
                }
            }
        ),
        403: "Only sponsors allowed",
        400: "Invalid request data"
    }
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sponsor_khalti_init(request):
    user = request.user

    # Only sponsors can initiate payment
    if not user.groups.filter(name="Sponsor").exists():
        return Response({"error": "Only sponsors allowed"}, status=403)

    try:
        student_id = request.data["student_id"]
        course_id = request.data["course_id"]
        amount = float(request.data["amount"])
    except (KeyError, ValueError):
        return Response({"error": "Invalid request data"}, status=400)

    # Create sponsorship record (pidx will be updated later)
    sponsorship = Sponsorship.objects.create(
        sponsor=user,
        student_id=student_id,
        course_id=course_id,
        amount=amount
    )

    # Prepare Khalti payload
    payload = {
        "return_url": "http://127.0.0.1:8000/api/payment/sponsor/verify/",
        "website_url": "http://127.0.0.1:8000/",
        "amount": int(amount * 100),  # convert NPR to paisa
        "purchase_order_id": str(sponsorship.id),
        "purchase_order_name": "Course Sponsorship",
    }

    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    # Call Khalti API
    try:
        response = requests.post(
            "https://a.khalti.com/api/v2/epayment/initiate/",
            json=payload,
            headers=headers
        )
        data = response.json()
    except Exception as e:
        return Response({"error": "Failed to contact Khalti", "details": str(e)}, status=500)

    # Save pidx to sponsorship
    sponsorship.pidx = data.get("pidx")
    sponsorship.save()

    return Response({"payment_url": data.get("payment_url")})

@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter(
            'pidx',
            openapi.IN_QUERY,
            description="Payment ID from Khalti",
            type=openapi.TYPE_STRING
        )
    ],
    responses={
        200: "Payment successful",
        400: "Payment failed or invalid pidx",
    }
)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sponsor_khalti_verify(request):
    pidx = request.GET.get("pidx")
    if not pidx:
        return Response({"error": "pidx is required"}, status=400)

    try:
        sponsorship = Sponsorship.objects.get(pidx=pidx)
    except Sponsorship.DoesNotExist:
        return Response({"error": "Invalid pidx"}, status=400)

    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            "https://khalti.com/api/v2/payment/verify/",  # Correct endpoint
            json={"token": pidx, "amount": int(sponsorship.amount * 100)},  # amount in paisa
            headers=headers
        )
        data = response.json()
    except requests.exceptions.RequestException as e:
        return Response({"error": "Failed to contact Khalti", "details": str(e)}, status=500)

    # Check payment status
    if data.get("state") == "Completed":
        sponsorship.status = "Completed"
        sponsorship.save()

        # Grant student access
        Enrollment.objects.get_or_create(
            student=sponsorship.student,
            course=sponsorship.course
        )

        return Response({"message": "Funding successful"}, status=200)
    else:
        sponsorship.status = "Failed"
        sponsorship.save()
        return Response({"message": "Payment failed"}, status=400)
