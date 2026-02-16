from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import RegisterForm
from .models import SOSAlert, SafeTrip, RouteFeedback, EmergencyContact, Incident
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm


def index(request):
    return render(request, "index.html")


def register_view(request):
    
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password1"]
        confirm_password = request.POST["password2"]

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            password=password
        )
        user.save()

        messages.success(request, "Account created successfully!")
        return redirect("login")

    return render(request, "register.html")




def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "login.html")


@login_required
def dashboard(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    trips = SafeTrip.objects.filter(user=request.user).order_by('-date')
    contacts = EmergencyContact.objects.filter(user=request.user)
    return render(request, "dashboard.html", {
        "profile": profile,
        "trips_count": trips.count(),
        "contacts": contacts
    })


@login_required
def profile_view(request):
    return render(request, "profile.html")


@login_required
def profile_edit_view(request):
    if request.method == "POST":
        user = request.user
        user.email = request.POST.get("email", user.email)
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.save()
        return redirect("profile")
    
    return render(request, "profile_edit.html")


from .models import SOSAlert, SafeTrip, Incident
from .forms import SafeTripForm
from django.db.models import Q

def analyze_safety(start, end, route_name):
    dangers = []
    recommendations = ["Stay alert and keep your phone charged."]
    score = 100
    
    text = (start + " " + end + " " + route_name).lower()
    
    # Check for reported incidents near the mentioned locations
    nearby_incidents = Incident.objects.filter(
        Q(location_name__icontains=start) | Q(location_name__icontains=end)
    )
    
    if nearby_incidents.exists():
        score -= 20
        dangers.append(f"Recent incidents reported near your locations ({nearby_incidents.count()} found)")
        recommendations.append("Check the live map for specific incident markers along your route.")

    if "park" in text:
        dangers.append("Isolated area, possible poor lighting")
        recommendations.append("Stick to well-lit paths and avoid shortcutting through bushes.")
        score -= 15
    if "bustop" in text or "bus stop" in text or "station" in text:
        dangers.append("Busy transport hub, possible pickpockets")
        recommendations.append("Keep your belongings secure and stay in crowded areas.")
        score -= 10
    if "night" in text or "evening" in text:
        dangers.append("Reduced visibility increases risk")
        recommendations.append("Share your live location with a trusted contact.")
        score -= 20
    if "market" in text or "mall" in text:
        dangers.append("High traffic area")
        recommendations.append("Be aware of your surroundings in large crowds.")
        score -= 5
    if "hospital" in text:
        recommendations.append("Emergency services are nearby.")
        score += 5

    return {
        "score": max(40, min(100, score)),
        "dangers": ", ".join(dangers) if dangers else "No major risks identified.",
        "recommendations": ". ".join(recommendations)
    }

@login_required
def safe_trips_view(request):
    if request.method == 'POST':
        form = SafeTripForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.user = request.user
            
            # Analyze safety before saving
            analysis = analyze_safety(trip.start_point, trip.end_point, trip.route_name)
            trip.safety_score = analysis['score']
            trip.danger_zones = analysis['dangers']
            trip.safety_recommendations = analysis['recommendations']
            trip.status = 'active'
            
            # Check community feedback for safety warnings
            safety_check = analyze_route_safety(trip.route_name)
            
            # If route is risky, show warning with alternatives
            if safety_check['rating'] in ['Risky', 'Medium']:
                # Get safer alternative routes
                alternatives = get_safer_alternatives(trip.route_name, trip.start_point, trip.end_point)
                
                if safety_check['rating'] == 'Risky':
                    messages.warning(
                        request, 
                        f"⚠️ SAFETY ALERT: The route '{trip.route_name}' has {safety_check['total_reports']} recent reports including harassment or unsafe incidents. "
                        f"{alternatives}"
                    )
                else:
                    messages.info(
                        request,
                        f"ℹ️ Safety Notice: '{trip.route_name}' has some safety concerns reported by the community. {alternatives}"
                    )
            
            trip.save()
            messages.success(request, f"Trip planned! Safety Score: {trip.safety_score}%")
            return redirect('safe_trips')
    else:
        form = SafeTripForm()

    trips = SafeTrip.objects.filter(user=request.user).order_by('-date')
    incidents = Incident.objects.all().order_by('-date')
    
    incidents_data = [
        {
            'lat': float(inc.latitude),
            'lon': float(inc.longitude),
            'type': inc.get_type_display(),
            'loc': inc.location_name,
            'desc': inc.description,
        }
        for inc in incidents
    ]
    
    feedbacks = RouteFeedback.objects.all().order_by('-created_at')
    
    # Analyze safety for each trip based on community feedback
    trips_with_analysis = []
    for trip in trips:
        safety_analysis = analyze_route_safety(trip.route_name)
        realtime_tips = get_realtime_safety_tips(trip.route_name, trip.start_point, trip.end_point, request.user)
        trips_with_analysis.append({
            'trip': trip,
            'safety_analysis': safety_analysis,
            'realtime_tips': realtime_tips
        })
    
    return render(request, "safe_trips.html", {
        "trips_with_analysis": trips_with_analysis,
        "form": form,
        "feedback_form": RouteFeedbackForm(),
        "feedbacks": feedbacks,
        "incidents_data": incidents_data
    })


@login_required
def safety_points_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    history = RedeemedReward.objects.filter(user=request.user).order_by('-date_redeemed')
    return render(request, "safety_points.html", {
        "profile": profile,
        "history": history
    })


from .models import SOSAlert, SafeTrip, Incident, EmergencyContact, UserProfile, RedeemedReward, RouteFeedback
from .forms import SafeTripForm, EmergencyContactForm, RouteFeedbackForm
from django.db.models import Q

# ... (analyze_safety remains unchanged)

@login_required
def sos_view(request):
    contacts = EmergencyContact.objects.filter(user=request.user)
    if request.method == "POST":
        if 'location' in request.POST:
            location = request.POST.get("location")
            SOSAlert.objects.create(user=request.user, location=location)
            messages.success(request, "SOS Alert sent to all emergency contacts!")
            return render(request, "sos.html", {"message": "SOS Sent Successfully!", "contacts": contacts, "form": EmergencyContactForm()})
        else:
            form = EmergencyContactForm(request.POST)
            if form.is_valid():
                contact = form.save(commit=False)
                contact.user = request.user
                contact.save()
                messages.success(request, "Emergency contact added successfully!")
                return redirect('sos')
    else:
        form = EmergencyContactForm()
    
    return render(request, "sos.html", {"contacts": contacts, "form": form})

@login_required
def delete_contact_view(request, contact_id):
    contact = EmergencyContact.objects.get(id=contact_id, user=request.user)
    contact.delete()
    messages.success(request, "Contact removed.")
    return redirect('sos')


@login_required
def complete_trip_view(request, trip_id):
    trip = SafeTrip.objects.get(id=trip_id, user=request.user)
    if trip.status != 'completed':
        trip.status = 'completed'
        trip.save()
        
        # Award points: Score / 10
        points_earned = int(trip.safety_score / 10)
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.safety_points += points_earned
        profile.safe_trips += 1
        profile.save()
        
        messages.success(request, f"Trip ended! You earned {points_earned} Safety Points! ⭐")
    
    return redirect('safe_trips')

@login_required
def redeem_reward_view(request, reward_id):
    rewards = {
        1: {'name': 'Free Meal', 'cost': 500},
        2: {'name': 'Movie Ticket', 'cost': 400},
        3: {'name': 'Coffee Card', 'cost': 300},
        4: {'name': 'Premium Headphones', 'cost': 1000},
        5: {'name': 'Shopping Voucher', 'cost': 750},
        6: {'name': 'Travel Discount', 'cost': 1500},
    }
    
    reward = rewards.get(reward_id)
    if not reward:
        messages.error(request, "Invalid reward.")
        return redirect('safety_points')
        
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if profile.safety_points >= reward['cost']:
        profile.safety_points -= reward['cost']
        profile.save()
        
        # Save redemption history
        RedeemedReward.objects.create(
            user=request.user,
            reward_name=reward['name'],
            points_spent=reward['cost']
        )
        
        messages.success(request, f"Success! You redeemed: {reward['name']} 🎁")
    else:
        messages.error(request, f"Insufficient points for {reward['name']}. Keep traveling safely!")
        
    return redirect('safety_points')

def logout_view(request):
    logout(request)
    return redirect("index")






@login_required
def add_feedback_view(request):
    if request.method == 'POST':
        form = RouteFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, "Thank you for your feedback! Your suggestion helps others.")
            return redirect('safe_trips')
    return redirect('safe_trips')


def analyze_route_safety(route_name):
    """
    Women Safety Advisor: Analyzes community feedback for a specific route.
    Returns a safety rating and summary based on reported issues.
    """
    # Get all feedback for this route (case-insensitive partial match)
    feedbacks = RouteFeedback.objects.filter(route_name__icontains=route_name)
    
    if not feedbacks.exists():
        return {
            'rating': 'Unknown',
            'rating_class': 'warning',
            'summary': 'No community feedback available for this route yet. Be the first to share your experience!',
            'total_reports': 0,
            'concerns': []
        }
    
    # Analyze feedback for safety concerns
    harassment_keywords = ['harassment', 'teasing', 'catcall', 'staring', 'following', 'uncomfortable']
    unsafe_keywords = ['unsafe', 'dangerous', 'risky', 'scared', 'afraid', 'threatened']
    suspicious_keywords = ['suspicious', 'lurking', 'gang', 'shady', 'creepy']
    
    harassment_count = 0
    unsafe_count = 0
    suspicious_count = 0
    concerns = []
    
    for fb in feedbacks:
        text = (fb.what_went_wrong + ' ' + fb.get_issue_category_display()).lower()
        
        if any(keyword in text for keyword in harassment_keywords):
            harassment_count += 1
            concerns.append(f"⚠️ Harassment reported by {fb.user.username}")
        
        if any(keyword in text for keyword in unsafe_keywords):
            unsafe_count += 1
            concerns.append(f"🚨 Unsafe situation reported by {fb.user.username}")
            
        if any(keyword in text for keyword in suspicious_keywords):
            suspicious_count += 1
            concerns.append(f"👁️ Suspicious activity reported by {fb.user.username}")
    
    total_reports = feedbacks.count()
    total_concerns = harassment_count + unsafe_count + suspicious_count
    
    # Determine safety rating
    if total_concerns == 0:
        rating = 'Safe'
        rating_class = 'success'
        summary = f"✅ This route has {total_reports} community report(s) with no safety concerns. Women users have not reported any harassment or unsafe situations."
    elif total_concerns <= 1 or (total_concerns / total_reports) < 0.3:
        rating = 'Medium'
        rating_class = 'warning'
        summary = f"⚠️ This route has some concerns. Out of {total_reports} reports, {total_concerns} mentioned safety issues. Exercise caution and consider traveling during daylight or with companions."
    else:
        rating = 'Risky'
        rating_class = 'danger'
        summary = f"🚨 CAUTION: This route has multiple safety concerns. {total_concerns} out of {total_reports} reports mentioned harassment, unsafe situations, or suspicious activities. Consider alternative routes."
    
    return {
        'rating': rating,
        'rating_class': rating_class,
        'summary': summary,
        'total_reports': total_reports,
        'harassment_count': harassment_count,
        'unsafe_count': unsafe_count,
        'suspicious_count': suspicious_count,
        'concerns': concerns[:5]  # Limit to 5 most recent concerns
    }


def get_safer_alternatives(risky_route, start_point, end_point):
    """
    Suggests safer alternative routes based on community feedback.
    Returns a string with alternative suggestions and reasons.
    """
    # Get all routes from feedback
    all_routes = RouteFeedback.objects.values_list('route_name', flat=True).distinct()
    
    # Analyze each route and find safer ones
    safer_routes = []
    for route in all_routes:
        if route.lower() != risky_route.lower():
            safety = analyze_route_safety(route)
            if safety['rating'] == 'Safe':
                safer_routes.append({
                    'name': route,
                    'rating': safety['rating'],
                    'reports': safety['total_reports']
                })
    
    # Build suggestion message
    if safer_routes:
        suggestions = []
        for alt in safer_routes[:2]:  # Show top 2 alternatives
            suggestions.append(f"'{alt['name']}' (Safe - {alt['reports']} positive community reports)")
        
        return f"Consider these safer alternatives: {', '.join(suggestions)}. These routes have no reports of harassment or unsafe incidents."
    else:
        # Generic safety advice if no specific alternatives found
        return (
            "We recommend: 1) Travel during daylight hours, 2) Share your live location with trusted contacts, "
            "3) Stay on well-lit main roads, 4) Use the SOS feature if you feel unsafe."
        )


def get_realtime_safety_tips(route_name, start_point, end_point, user):
    """
    Real-Time Women Safety Assistant: Provides context-aware safety suggestions
    based on current time (day/night) and location characteristics.
    """
    from datetime import datetime
    
    current_hour = datetime.now().hour
    is_night = current_hour >= 19 or current_hour < 6  # 7 PM to 6 AM
    is_evening = 17 <= current_hour < 19  # 5 PM to 7 PM
    
    tips = []
    priority_level = "normal"
    
    # Time-based suggestions
    if is_night:
        priority_level = "high"
        tips.extend([
            "🌙 **Night Travel Alert**: It's currently nighttime. Extra precautions recommended.",
            "💡 Stick to well-lit, main roads. Avoid shortcuts through dark alleys or parks.",
            "📱 Share your live location with a trusted contact immediately.",
            "👥 Travel in groups if possible, or use verified ride-sharing services.",
        ])
    elif is_evening:
        priority_level = "medium"
        tips.extend([
            "🌆 **Evening Hours**: Visibility is reducing. Stay alert.",
            "💡 Choose routes with good street lighting.",
            "📱 Consider sharing your live location with family or friends.",
        ])
    else:
        tips.extend([
            "☀️ **Daytime Travel**: Generally safer, but stay vigilant.",
            "👥 Prefer crowded, busy roads over isolated routes.",
        ])
    
    # Location-based suggestions
    location_text = f"{route_name} {start_point} {end_point}".lower()
    
    if any(word in location_text for word in ['park', 'garden', 'forest']):
        tips.append("🌳 **Park/Garden Route**: Avoid isolated paths. Stay on main walkways with visibility.")
        priority_level = "high" if is_night else "medium"
    
    if any(word in location_text for word in ['market', 'mall', 'bazaar', 'shopping']):
        tips.append("🛍️ **Crowded Area**: Good choice! Stay aware of pickpockets. Keep belongings secure.")
    
    if any(word in location_text for word in ['highway', 'main road', 'expressway']):
        tips.append("🛣️ **Main Road**: Excellent choice for safety. Well-lit and monitored.")
    
    if any(word in location_text for word in ['station', 'metro', 'bus stop', 'railway']):
        tips.append("🚉 **Transit Hub**: Stay in well-lit waiting areas. Avoid isolated platforms.")
    
    # Emergency contact reminder
    emergency_contacts = EmergencyContact.objects.filter(user=user).count()
    if emergency_contacts == 0:
        tips.append("⚠️ **No Emergency Contacts**: Add emergency contacts in your profile for quick SOS alerts.")
    else:
        tips.append(f"✅ **Emergency Contacts Ready**: You have {emergency_contacts} contact(s) set up for SOS alerts.")
    
    # General safety tips
    tips.extend([
        "📞 Keep your phone charged and easily accessible.",
        "🚨 Use the SOS button if you feel unsafe at any point.",
        "👀 Trust your instincts. If something feels wrong, find a safe public place.",
    ])
    
    return {
        'tips': tips,
        'priority_level': priority_level,
        'is_night': is_night,
        'time_context': 'Night' if is_night else ('Evening' if is_evening else 'Day')
    }


@login_required
def safety_survey_view(request, trip_id):
    """
    Safety Survey: Collect detailed feedback about route experience.
    """
    from .forms import SafetySurveyForm
    from .models import SafetySurvey
    
    trip = SafeTrip.objects.get(id=trip_id, user=request.user)
    
    if request.method == 'POST':
        form = SafetySurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.user = request.user
            survey.trip = trip
            survey.route_name = trip.route_name
            survey.save()
            messages.success(request, "Thank you for completing the safety survey! Your feedback helps keep other women safe.")
            return redirect('safe_trips')
    else:
        form = SafetySurveyForm(initial={'route_name': trip.route_name})
    
    return render(request, 'safety_survey.html', {
        'form': form,
        'trip': trip
    })
