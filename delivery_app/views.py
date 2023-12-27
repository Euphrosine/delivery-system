from rest_framework import viewsets
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from .models import DeliveryRequest, DeliverySentForm
from .serializers import UserSerializer,DeliveryRequestSerializer, DeliverySentFormSerializer

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
        account_sid = 'ACb5922573b89ddb0390647bc72f6db227'
        auth_token = 'e1a3626ec3b28f06e5490c01df6b36a6'

        # Comment the following line if you're not using a proxy
        # http_client = TwilioHttpClient(proxy={'http': settings.PROXY_URL, 'https': settings.PROXY_URL})
        
        client = Client(account_sid, auth_token)  # Remove http_client parameter

        # Replace the placeholders with actual data from the instance
        message_body = f'New order received! Customer: {instance.customer_name}, Contact: {instance.contact_number}, Delivery Date: {instance.delivery_date}'

        # Send WhatsApp message
        message = client.messages.create(
            from_='whatsapp:+14155238886',  # Replace with your Twilio sandbox WhatsApp number
            body=message_body,
            to=f'whatsapp:+250785437037'
        )

        print(f'WhatsApp message sent! SID: {message.sid}')

    def send_email_notification(self, instance):
        # Replace the placeholders with actual data from the instance
        subject = 'New Order Received'
        message = f'New order received!\nCustomer: {instance.customer_name}\nContact: {instance.contact_number}\nDelivery Date: {instance.delivery_date}'
        from_email = 'djangodev05@gmail.com'
        recipient_list = ['euphrosine46@gmail.com']

        # Send email
        send_mail(subject, message, from_email, recipient_list)

        print('Email sent!')

# Sent delivery
class DeliverySentFormViewSet(viewsets.ModelViewSet):
    queryset = DeliverySentForm.objects.all()
    serializer_class = DeliverySentFormSerializer

    def perform_create(self, serializer):
        instance = serializer.save()

        # Send notifications
        self.send_notifications(instance)

    def send_notifications(self, instance):
        # Send WhatsApp message and email notifications to the receiver
        receiver_notification_message = f"Your delivery request has been accepted. It is now being transported by {instance.transporter_name} ({instance.transporter_contact})."
        self.send_whatsapp_message(instance.customer_contact, receiver_notification_message)
        self.send_email_notification(instance.customer_email, receiver_notification_message)

        # Send email notifications to the order person
        order_person_notification_message = f"The delivery request from {instance.customer_name} has been sent. It is being transported by {instance.transporter_name} ({instance.transporter_contact}) to {instance.delivery_address}."
        self.send_email_notification('djangodev05@gmail.com', order_person_notification_message)

    def send_whatsapp_message(self, contact_number, message):
        # Your Twilio Account SID and Auth Token
        account_sid = 'ACb5922573b89ddb0390647bc72f6db227'
        auth_token = 'e1a3626ec3b28f06e5490c01df6b36a6'

        # Comment the following line if you're not using a proxy
        # http_client = TwilioHttpClient(proxy={'http': settings.PROXY_URL, 'https': settings.PROXY_URL})
        
        client = Client(account_sid, auth_token)  # Remove http_client parameter

        # Replace the placeholders with actual data from the instance
        message_body = message

        # Send WhatsApp message
        message = client.messages.create(
            from_='whatsapp:+14155238886',  # Replace with your Twilio sandbox WhatsApp number
            body=message_body,
            to=f'whatsapp:{contact_number}'
        )
        print(f'WhatsApp message sent to {contact_number}! SID: {message.sid}')

    def send_email_notification(self, to_email, message):
        # Replace the placeholders with actual data from the instance
        subject = 'Delivery Notification'
        message = message
        from_email = 'djangodev05@gmail.com'  # Replace with your email
        recipient_list = [to_email]

        # Send email
        send_mail(subject, message, from_email, recipient_list)

        print(f'Email sent to {to_email}!')
