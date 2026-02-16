from django.contrib import admin
from .models import SOSAlert, UserProfile, EmergencyContact, SafeTrip, Incident, RedeemedReward, RouteFeedback, SafetySurvey

admin.site.register(SOSAlert)
admin.site.register(UserProfile)
admin.site.register(EmergencyContact)
admin.site.register(SafeTrip)
admin.site.register(Incident)
admin.site.register(RedeemedReward)
admin.site.register(RouteFeedback)
admin.site.register(SafetySurvey)
