from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404, redirect
from .models import Patient, PredictionHistory
import pickle
import numpy as np
import random
import os
from sklearn.linear_model import LinearRegression
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt




# Load model once globally to avoid repeated file access
model_file_path = 'C:\\Users\\tinotenda.bininga\\OneDrive - TSL Ltd\\Desktop\\zvani\\Zvandiri_System\\model.pkl'
ml_model = None

def load_model():
    global ml_model
    if ml_model is None and os.path.exists(model_file_path):
        with open(model_file_path, 'rb') as file:
            ml_model = pickle.load(file)
    return ml_model

recommendation_pools = {
    "VL_Count": {
        0: ["The patient is virally suppressed. Continue monitoring regularly.",
            "Consider reducing the frequency of clinical visits if the patient remains stable.",
            "Encourage continued adherence to maintain viral suppression."],
        1: ["The patient is not virally suppressed. Intensify adherence support.",
            "Consider switching to a second-line regimen if suppression is not achieved soon.",
            "Arrange a follow-up viral load test in 3 months."]
    },
    "Attended_Last_Clinical_Appointment": {
        0: ["The patient missed the last clinical appointment. Schedule a follow-up visit.",
            "Provide reminders to help the patient stay on track with clinical visits.",
            "Investigate potential barriers that may be causing missed appointments."],
        1: ["The patient is attending regular clinical appointments. Keep up the good work.",
            "Continue monitoring adherence and viral load during future appointments.",
            "Encourage the patient to maintain regular clinic visits."]
    },
    "Gender": {
        0: ["Provide sexual and reproductive health education specific to women.",
            "If pregnant or breastfeeding, offer maternal health services.",
            "Consider additional screenings for cervical cancer."],
        1: ["Encourage routine health check-ups tailored to men's health.",
            "Consider discussions around sexual health, especially if the patient is sexually active.",
            "Provide mental health support if necessary, especially for younger men."]
    },
    "MH": {
        0: ["The patient has no immediate mental health concerns.",
            "Encourage ongoing support through community activities to maintain mental well-being.",
            "No mental health interventions are required at this time."],
        1: ["The patient is at risk for mental health issues. Refer to mental health services.",
            "Monitor the patient's mental health regularly.",
            "Consider a mental health assessment to determine the level of support needed."]
    },
    "Breast_Lactating": {
        0: ["Breastfeeding is not currently relevant for this patient.",
            "No maternal health interventions are needed at this time.",
            "Ensure general reproductive health education."],
        1: ["Provide breastfeeding counseling and support.",
            "Ensure maternal health services are available for the patient.",
            "Check if the patient needs nutritional supplements."]
    },
    "Pregnant": {
        0: ["The patient is not pregnant, continue routine care.",
            "No pregnancy-related interventions are needed at this time.",
            "Focus on other aspects of the patient's health."],
        1: ["Provide prenatal care and monitor the pregnancy closely.",
            "Discuss potential birth plans and postnatal care.",
            "Ensure the patient has access to maternal healthcare services."]
    }
}



# Login view
def login_view(request):
    if request.user.is_authenticated:  # If user is already logged in, redirect to dashboard
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to dashboard after login
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')  # Render login template

# Signup view
def signup_view(request):
    if request.user.is_authenticated:  # If user is already logged in, redirect to dashboard
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')  # Redirect to login after successful signup
        except:
            messages.error(request, 'Failed to create account. Username might be taken.')
    return render(request, 'signup.html')  # Render signup template

# Logout view
def logout_view(request):
    logout(request)
    return redirect('login.html')  # Redirect to login page after logout


from django.shortcuts import render, get_object_or_404, redirect
from .models import PredictionHistory
from .forms import PatientForm  # A form we will create for editing

# View to edit a patient
def edit_patient(request, patient_id):
    patient = get_object_or_404(PredictionHistory, id=patient_id)

    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Redirect back to the dashboard after saving
    else:
        form = PatientForm(instance=patient)

    return render(request, 'edit_patient.html', {'form': form, 'patient': patient})

# View to delete a patient
def delete_patient(request, patient_id):
    patient = get_object_or_404(PredictionHistory, id=patient_id)
    if request.method == 'POST':
        patient.delete()
        return redirect('dashboard')  # Redirect back to the dashboard after deletion
    return render(request, 'delete_patient.html', {'patient': patient})



# Dashboard view (requires login)
@login_required(login_url='login')  # Redirect to login page if not authenticated
def dashboard(request):
    history = PredictionHistory.objects.all().order_by('-date')
    
    # List of possible locations
    locations = ['Harare', 'Gweru', 'Masvingo', 'Bulawayo', 'Mutare', 'Marondera']

    # Get all prediction history records
    prediction_history = PredictionHistory.objects.all()

    # Create a list of patients with random age, location, and status
    patient_list = [
        {
            'patient_id': history.id,
            'patient': history.patient,
            'age': random.randint(0, 20),  # Generate random age between 20 and 80
            'gender': history.gender,
            'phone_number': generate_phone_number(), 
            'location': random.choice(locations),  # Randomly assign location
            'prediction_history': history.prediction_text,
        }
        for history in prediction_history
    ]

    # Pagination for the prediction history (5 items per page)
    paginator = Paginator(prediction_history, 5)  # Paginate history only, not patient list
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except:
        page_obj = None  # If pagination fails or no page is provided, set page_obj to None

    # Context to be passed to the template
    context = {
        'page_obj': page_obj,  # Paginated history
        'patient_list': patient_list,  # Only show the 5 most recent patients
    }
    
    return render(request, 'dashboard.html', {'history': history,'page_obj': page_obj,'patient_list': patient_list})


def home(request):
    return render(request, 'index.html')


from django.http import JsonResponse
import random
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def chatbot_view(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').lower()

        # Enhanced Menu options to guide the user
        menu = (
            '<div class="bot-message" style="border: 1px solid #28a745; border-radius: 8px; padding: 15px; background-color: #f9f9f9; font-family: Arial, sans-serif;">'
            '<strong style="font-size: 1.5em; color: #28a745;">Hello, I\'m Bheki!</strong>'
            '<p style="font-size: 1.1em;">How can I assist you today?</p>'
            '<strong style="font-size: 1.2em;">Please choose one of the options below:</strong>'
            '<ul style="list-style-type: none; padding: 0; margin: 10px 0;">'
            '<li style="margin: 5px 0;"><strong>1.</strong> 📝 <span style="color: #555;">View Patient List</span></li>'
            '<li style="margin: 5px 0;"><strong>2.</strong> 📊 <span style="color: #555;">Check Patient Predictions</span></li>'
            '<li style="margin: 5px 0;"><strong>3.</strong> 🛠️ <span style="color: #555;">Help with the Dashboard</span></li>'
            '<li style="margin: 5px 0;"><strong>4.</strong> 📈 <span style="color: #555;">View System Statistics</span></li>'
            '<li style="margin: 5px 0;"><strong>5.</strong> 🧬 <span style="color: #555;">Learn about Viral Load Count</span></li>'
            '<li style="margin: 5px 0;"><strong>6.</strong> 💡 <span style="color: #555;">Mental Health Support Information</span></li>'
            '<li style="margin: 5px 0;"><strong>7.</strong> 🚪 <span style="color: #555;">Exit</span></li>'
            '</ul>'
            '<p style="font-size: 1.1em; color: #555;">👉 Please enter the number of your choice:</p>'
            '</div>'
        )

        # Default response for the first interaction
        if user_message in ['hello', 'hi', 'hey']:
            response = f"{menu}\nPlease enter the number of your choice."

        # Handling numbered inputs from the user, converted to questions
        elif user_message == '1':
            response = random.choice([
                "Would you like to view the patient list on the dashboard?",
                "Should I guide you to the patient list section in the dashboard?"
            ])
        elif user_message == '2':
            response = random.choice([
                "Do you want to check patient predictions in the 'Predictions' tab?",
                "Shall I assist you in accessing the 'Patient Care Prediction' section?"
            ])
        elif user_message == '3':
            response = "Do you need help navigating the dashboard features?"
        elif user_message == '4':
            response = (
                "Would you like to view system statistics? Here are the current stats:\n"
                "- Total Patients: 120\n"
                "- Patients with Suppressed Viral Load: 85\n"
                "- Patients needing follow-up: 35\n"
                "- Clinical appointments missed: 12"
            )
        elif user_message == '5':
            response = (
                "Are you interested in learning more about the viral load count?\n"
                "A suppressed viral load indicates effective treatment. Would you like more details?"
            )
        elif user_message == '6':
            response = (
                "Are you looking for mental health support information?\n"
                "I can help refer patients flagged for mental health concerns. Should I continue?"
            )
        elif user_message == '7':
            response = "Are you sure you want to exit? Feel free to return anytime! 👋"

        # If user input is not recognized
        else:
            response = (
                "I didn't quite catch that. Please select a valid option:\n"
                f"{menu}\nEnter the number of your choice."
            )

        return JsonResponse({'message': response})

    # Initial GET request welcome message
    return JsonResponse({'message': "Welcome to the Bheki chatbot! Type 'hello' to start. 😊"})




def generate_phone_number():
    """Generate a random 11-digit Zimbabwean phone number."""
    return "077" + "".join([str(random.randint(0, 9)) for _ in range(8)])


def generate_random_patient_name():
    # Generate a random patient name like "Patient 1", "Patient 2", etc.
    random_number = random.randint(1, 1000)
    return f"Patient {random_number}"

def result(request):
    if request.method == 'GET':
        # Get input values
        patient_name = request.GET.get('patient_name', '')  # Get the patient's name
        VL_Count = request.GET.get('VL_Count', 'no')
        attended_last_appointment = request.GET.get('Attended_Last_Clinical_Appointment', 'no')
        gender = request.GET.get('Gender', 'female')  # Default is 'female'
        mh = request.GET.get('MH', 'no')
        breastfeeding = request.GET.get('Breast_Lactating', 'no')
        pregnant = request.GET.get('Pregnant', 'no')

        # Convert inputs to numerical values
        vl_count = 1 if VL_Count.lower() == 'no' else 0
        attended_last = 1 if attended_last_appointment.lower() == 'yes' else 0
        mh_value = 1 if mh.lower() == 'yes' else 0
        breastfeeding_value = 1 if breastfeeding.lower() == 'yes' else 0
        pregnant_value = 1 if pregnant.lower() == 'yes' else 0

        # Keep gender as 'Male' or 'Female'
        gender_label = 'Male' if gender.lower() == 'male' else 'Female'

        # Define features array
        features = np.array([[vl_count, attended_last, 1 if gender_label == 'Male' else 0, mh_value, breastfeeding_value, pregnant_value]])

        # Load and make prediction
        ml_model = load_model()
        if ml_model is not None:
            prediction = ml_model.predict(features)
            prediction_text = "Enhanced Care" if prediction[0] == 1 else "Standard Care"

            # Generate recommendations
            try:
                vl_recommendations = random.sample(recommendation_pools["VL_Count"][vl_count], 1)
                attended_recommendations = random.sample(recommendation_pools["Attended_Last_Clinical_Appointment"][attended_last], 1)
                gender_recommendations = random.sample(recommendation_pools["Gender"][1 if gender_label == 'Male' else 0], 1)
                mh_recommendations = random.sample(recommendation_pools["MH"][mh_value], 1)
                breastfeeding_recommendations = random.sample(recommendation_pools["Breast_Lactating"][breastfeeding_value], 1)
                pregnancy_recommendations = random.sample(recommendation_pools["Pregnant"][pregnant_value], 1)

                recommendations = vl_recommendations + attended_recommendations + gender_recommendations + mh_recommendations + breastfeeding_recommendations + pregnancy_recommendations

            except KeyError as e:
                return render(request, 'result.html', {'error': f'Missing recommendation for {str(e)}'})

            # Generate random age and location
            random_age = random.randint(0, 20)
            random_location = random.choice(['Harare', 'Gweru', 'Masvingo', 'Bulawayo', 'Mutare', 'Marondera'])

            # Save prediction and recommendations to PredictionHistory
            PredictionHistory.objects.create(
                patient=patient_name,
                gender=gender_label,
                prediction_text=prediction_text,
                recommendations=recommendations
            )

            return render(request, 'result.html', {
                'classification': prediction_text,
                'recommendations': recommendations,
                'patient_name': patient_name,
                'age': random_age,
                'location': random_location,
            })
        else:
            return render(request, 'result.html', {'error': 'Error loading model!'})
