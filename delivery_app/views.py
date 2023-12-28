from rest_framework import viewsets
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from .models import DeliveryRequest, DeliverySentForm
from .serializers import UserSerializer,DeliveryRequestSerializer, DeliverySentFormSerializer
from decouple import config
from django.core.mail import EmailMessage
from django.urls import reverse

# User authentication
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import authentication_classes, permission_classes




# user authentication
class UserSignupView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user_id': user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user_id': user.id}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# Request delivery
@authentication_classes([])
@permission_classes([AllowAny])
class DeliveryRequestViewSet(viewsets.ModelViewSet):
    queryset = DeliveryRequest.objects.all()
    serializer_class = DeliveryRequestSerializer

    def perform_create(self, serializer):
        # Call the original perform_create method to save the instance
        instance = serializer.save()

        # Send WhatsApp message
        self.send_whatsapp_message(instance)

        # Send email notification
        self.send_email_notification(instance)

    def send_whatsapp_message(self, instance):
        # Your Twilio Account SID and Auth Token
        account_sid = config('TWILIO_ACCOUNT_SID')
        auth_token = config('TWILIO_AUTH_TOKEN')
        twilio_whatsapp_number = config('TWILIO_WHATSAPP_NUMBER')


        # Comment the following line if you're not using a proxy
        # http_client = TwilioHttpClient(proxy={'http': settings.PROXY_URL, 'https': settings.PROXY_URL})
        
        client = Client(account_sid, auth_token)  # Remove http_client parameter

        # Replace the placeholders with actual data from the instance
        message_body = f'New order received! Customer: {instance.customer_name}, Contact: {instance.contact_number}, Delivery Date: {instance.delivery_date}'

        # Send WhatsApp message
        message = client.messages.create(
            from_=twilio_whatsapp_number,
            body=message_body,
            to=f'whatsapp:+250785437037'  # Replace with config('RECEIVER_PHONE_NUMBER')
        )

        print(f'WhatsApp message sent! SID: {message.sid}')


    def send_email_notification(self, instance):
        # Replace the placeholders with actual data from the instance
        subject = 'New Order Received'
        message = f'New order received!\nCustomer: {instance.customer_name}\nContact: {instance.contact_number}\nDelivery Date: {instance.delivery_date}'

        # Replace email addresses with environment variables
        from_email = config('EMAIL_FROM')
        recipient_list = [config('EMAIL_TO')]

        # Send email
        send_mail(subject, message, from_email, recipient_list)

        print('Email sent!')

@authentication_classes([])
@permission_classes([AllowAny])
# Sent delivery
class DeliverySentFormViewSet(viewsets.ModelViewSet):
    queryset = DeliverySentForm.objects.all()
    serializer_class = DeliverySentFormSerializer

    def perform_create(self, serializer):
        # Handle image upload separately
        image_file = self.request.data.get('image')
        instance = serializer.save(image=image_file)

        # Send notifications
        self.send_notifications(instance, image_data=image_file.read(), image_name=image_file.name)
        

    def send_notifications(self, instance, image_data=None, image_name=None):
        # Send WhatsApp message and email notifications to the receiver
        receiver_notification_message = f"Your delivery request has been accepted. It is now being transported by {instance.transporter_name} ({instance.transporter_contact})."
        self.send_whatsapp_message(instance.customer_contact, receiver_notification_message, image_data=image_data)
        self.send_email_notification(instance.customer_email, receiver_notification_message, image_data=image_data, image_name=image_name)

        # Send email notifications to the order person
        order_person_notification_message = f"The delivery request from {instance.customer_name} has been sent. It is being transported by {instance.transporter_name} ({instance.transporter_contact}) to {instance.delivery_address}."
        self.send_email_notification('djangodev05@gmail.com', order_person_notification_message, image_data=image_data, image_name=image_name)

    def send_whatsapp_message(self, contact_number, message, image_data=None):
        # Your Twilio Account SID and Auth Token
        account_sid = config('TWILIO_ACCOUNT_SID')
        auth_token = config('TWILIO_AUTH_TOKEN')
        twilio_whatsapp_number = config('TWILIO_WHATSAPP_NUMBER')

        client = Client(account_sid, auth_token)

        # Include image in the message if available
        if image_data:
            message += f'\nImage attached'

        # Send WhatsApp message
        message = client.messages.create(
            from_=twilio_whatsapp_number,
            body=message,
            to=f'whatsapp:{contact_number}'
        )
        print(f'WhatsApp message sent to {contact_number}! SID: {message.sid}')

    def send_email_notification(self, to_email, message, image_data=None, image_name=None):
        # Replace the placeholders with actual data from the instance
        subject = 'Delivery Notification'
        from_email = config('EMAIL_FROM')
        recipient_list = [to_email]

        # Create EmailMessage instance
        email = EmailMessage(subject, message, from_email, recipient_list)

        # Attach image to the email, if available
        if image_data and image_name:
            email.attach(image_name, image_data, 'image/png')  # Update the content type as per your image type

        # Send email
        email.send()

        print(f'Email sent to {to_email}!')


from django.http import FileResponse
from django.shortcuts import get_object_or_404
from .models import DeliverySentForm

def serve_uploaded_image(request, pk):
    instance = get_object_or_404(DeliverySentForm, pk=pk)
    response = FileResponse(instance.image)
    return response
