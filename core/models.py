from django.db import models
from django.contrib.auth.models import User


class SOSAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SOS by {self.user.username}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=100, blank=True)
    safe_trips = models.IntegerField(default=0)
    safety_points = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class EmergencyContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name



class SafeTrip(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')
    route_name = models.CharField(max_length=255)
    start_point = models.CharField(max_length=255)
    end_point = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    date = models.DateTimeField(auto_now_add=True)
    duration = models.CharField(max_length=50, blank=True)
    distance = models.CharField(max_length=50, blank=True)
    safety_score = models.IntegerField(default=100)
    danger_zones = models.TextField(blank=True, help_text="List of identified risky areas or factors")
    safety_recommendations = models.TextField(blank=True, help_text="Suggestions for a safer journey")

    def __str__(self):
        return f"{self.route_name} ({self.user.username})"

class Incident(models.Model):
    INCIDENT_TYPES = [
        ('theft', 'Theft/Robbery'),
        ('harassment', 'Harassment'),
        ('lighting', 'Poor Lighting'),
        ('accident', 'Accident'),
        ('other', 'Other'),
    ]

    type = models.CharField(max_length=20, choices=INCIDENT_TYPES)
    location_name = models.CharField(max_length=255)
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} at {self.location_name}"
class RedeemedReward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reward_name = models.CharField(max_length=100)
    points_spent = models.IntegerField()
    date_redeemed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.reward_name}"


class RouteFeedback(models.Model):
    ISSUE_CATEGORIES = [
        ('lighting', 'Poor Lighting'),
        ('safety', 'Safety Concern'),
        ('traffic', 'Heavy Traffic'),
        ('road', 'Bad Road Quality'),
        ('isolated', 'Isolated Area'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    route_name = models.CharField(max_length=255)
    issue_category = models.CharField(max_length=20, choices=ISSUE_CATEGORIES)
    what_went_wrong = models.TextField(help_text="Describe the bad experience you had")
    suggested_alternative = models.TextField(help_text="Suggest a better or safer route for others")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.route_name} feedback"


class SafetySurvey(models.Model):
    """
    Comprehensive safety survey for route experiences.
    Collects detailed feedback on lighting, crowds, harassment, and overall safety.
    """
    RATING_CHOICES = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    CROWD_LEVEL_CHOICES = [
        ('empty', 'Empty/Deserted'),
        ('few', 'Few People'),
        ('moderate', 'Moderately Crowded'),
        ('crowded', 'Very Crowded'),
    ]
    
    YES_NO_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trip = models.ForeignKey(SafeTrip, on_delete=models.CASCADE, null=True, blank=True)
    route_name = models.CharField(max_length=255)
    
    # Lighting Assessment
    lighting_rating = models.IntegerField(choices=RATING_CHOICES, help_text="How well-lit was the route?")
    
    # Crowd Level
    crowd_level = models.CharField(max_length=20, choices=CROWD_LEVEL_CHOICES, help_text="How crowded was the route?")
    
    # Harassment & Safety Incidents
    experienced_harassment = models.CharField(max_length=3, choices=YES_NO_CHOICES, help_text="Did you experience any harassment?")
    harassment_details = models.TextField(blank=True, help_text="If yes, please describe (optional)")
    
    experienced_teasing = models.CharField(max_length=3, choices=YES_NO_CHOICES, help_text="Did you experience catcalling or teasing?")
    teasing_details = models.TextField(blank=True, help_text="If yes, please describe (optional)")
    
    felt_unsafe = models.CharField(max_length=3, choices=YES_NO_CHOICES, help_text="Did you feel unsafe at any point?")
    unsafe_details = models.TextField(blank=True, help_text="If yes, please describe what made you feel unsafe (optional)")
    
    # Overall Safety Rating
    overall_safety_rating = models.IntegerField(choices=RATING_CHOICES, help_text="Overall, how safe did you feel on this route?")
    
    # Additional Comments
    additional_comments = models.TextField(blank=True, help_text="Any other feedback or suggestions?")
    
    # Metadata
    time_of_travel = models.CharField(max_length=20, choices=[
        ('morning', 'Morning (6 AM - 12 PM)'),
        ('afternoon', 'Afternoon (12 PM - 5 PM)'),
        ('evening', 'Evening (5 PM - 8 PM)'),
        ('night', 'Night (8 PM - 6 AM)'),
    ], help_text="When did you travel?")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.route_name} survey"
    
    class Meta:
        verbose_name = "Safety Survey"
        verbose_name_plural = "Safety Surveys"
