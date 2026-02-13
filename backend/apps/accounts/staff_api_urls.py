from django.urls import path

from .views import (
    StaffAggregateMissedView,
    StaffParentSessionsView,
    StaffParentsView,
    StaffPasswordResetView,
)

urlpatterns = [
    path("staff/password-reset/", StaffPasswordResetView.as_view(), name="staff-password-reset"),
    path("staff/parents/", StaffParentsView.as_view(), name="staff-parents"),
    path("staff/parents/<int:parent_id>/sessions/", StaffParentSessionsView.as_view(), name="staff-parent-sessions"),
    path(
        "staff/centres/<int:centre_id>/aggregate-missed/",
        StaffAggregateMissedView.as_view(),
        name="staff-centre-aggregate-missed",
    ),
]
