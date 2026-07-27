import json
import logging
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review

logger = logging.getLogger(__name__)

@csrf_exempt
def login_user(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

def logout_request(request):
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)

@csrf_exempt
def registration(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    
    username_exist = False
    try:
        User.objects.get(username=username)
        username_exist = True
    except User.DoesNotExist:
        logger.debug("{} is new user".format(username))

    if not username_exist:
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email
        )
        login(request, user)
        return JsonResponse({"userName": username, "status": "Authenticated"})
    else:
        return JsonResponse({"userName": username, "error": "Already Registered"})

def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels": cars})

# Update get_dealerships to render list of dealerships (all by default, or by state)
def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})

# Get dealer details by dealer_id
def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchDealer/" + str(dealer_id)
        dealership = get_request(endpoint)
        
        # If Mongo/Express returned a list, grab the first item
        if isinstance(dealership, list) and len(dealership) > 0:
            dealership = dealership[0]
            
        return JsonResponse({"status": 200, "dealer": dealership})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})

# Get dealer reviews and analyze their sentiments
# Get dealer reviews and analyze their sentiments
def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchReviews/dealer/" + str(dealer_id)
        reviews = get_request(endpoint)
        
        # Ensure reviews is a list before iterating
        if isinstance(reviews, list):
            for review_detail in reviews:
                try:
                    response = analyze_review_sentiments(review_detail.get('review', ''))
                    if response and 'sentiment' in response:
                        review_detail['sentiment'] = response['sentiment']
                    else:
                        review_detail['sentiment'] = "neutral"
                except Exception as e:
                    logger.error(f"Sentiment analysis failed: {e}")
                    review_detail['sentiment'] = "neutral"
                    
            return JsonResponse({"status": 200, "reviews": reviews})
        else:
            return JsonResponse({"status": 200, "reviews": []})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})

# Add a review view method
@csrf_exempt
def add_review(request):
    if not request.user.is_anonymous:
        data = json.loads(request.body)
        try:
            post_review(data)
            return JsonResponse({"status": 200})
        except Exception as err:
            return JsonResponse({"status": 401, "message": f"Error in posting review: {err}"})
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})