from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from django.http import HttpResponseRedirect,HttpResponse
from .models import profile
from django.contrib.auth.decorators import login_required
from .form import UploadImageForm
from .models import Image,Disease
import tensorflow as tf
from keras.models import load_model
import numpy as np
import pickle
import pandas as pd
from sklearn.impute import SimpleImputer
import sklearn
from django.conf import settings
from joblib import load
from django.utils.safestring import mark_safe



# model = load_model(r'accounts\\Models\\disease_detection.keras')
# Create your views here.
def home(request):
    return render(request,'index.html')

# Create your views here.
def register(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        c_password = request.POST.get('Cpassword')
        user_obj = User.objects.filter(username = email)

        if password != c_password:
            messages.warning(request, "Password does'nt matches")
            return HttpResponseRedirect(request.path_info)

        if user_obj.exists():
            messages.warning(request, 'Email is already taken.')
            return HttpResponseRedirect(request.path_info)

        print(email)

        user_obj = User.objects.create(first_name = username , email = email , username = email)
        user_obj.set_password(password)
        user_obj.save()

        messages.success(request, 'Successfully Registered.')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'regis.html')


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username=email)

        if not user_obj.exists():
            messages.warning(request, 'Account not found.')
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username=email, password=password)
        if user_obj:
            login(request, user_obj)
            return redirect('/')
        messages.warning(request, 'Invalid credentials')
        return HttpResponseRedirect(request.path_info)

    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    # Optionally add logic here, e.g., messages or redirects
    return redirect('/')

@login_required
def upload(request):
    return render(request, 'upload.html')

@login_required
def type(request):
    return render(request, 'plant_type.html')

@login_required
def board(request):
    diseases = Disease.objects.filter(image__user=request.user)
    user = request.user
    return render(request, 'dashbord.html', {'diseases': diseases,'user':user})


class_names = ['Apple : Apple scab', 'Apple : Black rot', 'Apple : Cedar rust', 'Apple : Healthy',
               'Corn : Gray leaf spot', 'Corn : Common rust', 'Corn : Northern Leaf Blight', 'Corn : Healthy',
               'Grape : Black rot', 'Grape : Black Measles',  'Grape : Isariopsis Leaf Spot','Grape : Healthy',
               'Potato : Early blight',  'Potato : Late blight','Potato : Healthy',
               'Tomato : Bacterial spot', 'Tomato : Early blight', 'Tomato : Late blight', 'Tomato : Leaf Mold', 'Tomato : Yellow leaf curl virus', 'Tomato : Healthy'
               ]

def preprocess_image(image_path):
    img = tf.keras.preprocessing.image.load_img(image_path, target_size=(256, 256))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Create batch axis
    return img_array

# def upload_image( request):
#     if request.method == 'POST':
#         form = UploadImageForm(request.POST, request.FILES)
#         if form.is_valid():
#             image_file = form.cleaned_data['image']
#             image_name = image_file.name  # Generate a unique filename (optional)


#             # Save image to database (assuming 'Image' model is defined)
#             user = request.user
#             image = Image(user = user,image=image_file)
#             image.save()
#             image_name.replace(' ', '-')
#             image_path = f'public\\static\\disease_images\\{image_name}'
#             image_array = preprocess_image(image_path)
#             print("IMAGE PATH IS :",image_path)
#             predictions = model.predict(image_array)
#             predicted_class_index = np.argmax(predictions[0])
#             predicted_class = class_names[predicted_class_index]
#             disease = Disease(disease=predicted_class, image=image)
#             disease.save()
#             disease_id = disease.id
#             disease = Disease.objects.get(pk=disease_id)
#             image_url = disease.image.image.url


#             return render(request, 'upload.html' ,  {'predicted_disease': predicted_class, 'url': image_url})
#     else:
#         form = UploadImageForm()

#     return render(request, 'upload.html', {'form': form})

def Crop_Recommendation(request):
    recommended_crop = ''
    if request.method == 'POST':
        nitrogen=request.POST.get('nitrogen')
        phosphorus = request.POST.get('phosphorus')
        potassium = request.POST.get('potassium')
        temperature = request.POST.get('temperature')
        humidity = request.POST.get('humidity')
        phLevel = request.POST.get('phLevel')
        rainfall = request.POST.get('rainfall')

        RF_joblib = r'accounts\\Models\\RandomForest.pkl'
        loaded_RF_model = load(RF_joblib)
        new_data = np.array([[nitrogen, phosphorus, potassium, temperature, humidity, phLevel, rainfall]])
        recommended_crop = loaded_RF_model.predict(new_data)
        recommended_crop = recommended_crop[0]

    return render(request, 'crop_rec.html',{'crop': recommended_crop})

