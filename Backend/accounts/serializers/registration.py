from rest_framework import serializers
from accounts.models import User
from NaijaBay.utils import NOT_ALLOWED_EMAIL_DOMAINS, NOT_ALLOWED_USERNAMES
from allauth.account.utils import setup_user_email


# Register Serializer
class CustomRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, max_length=254, style={'input_type': 'email'})
    username = serializers.CharField(write_only=True, max_length=15)
    password1 = serializers.CharField(write_only=True, min_length=8, max_length=16, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, min_length=8, max_length=16, style={'input_type': 'password'})


    # Validate Username
    def validate_username(self, username):
        username = username.strip().lower()

        if not username.isalpha():
            raise serializers.ValidationError("Username must be alphabet characters only.")

        if username in NOT_ALLOWED_USERNAMES:
            raise serializers.ValidationError("Username is not allowed, try again.")

        existing_user = User.objects.filter(username=username)
        
        if existing_user.exists():
            raise serializers.ValidationError("Username already exists.")

        return username

    # Validate email
    def validate_email(self, email):
        email = email.strip().lower()

        if email.endswith(tuple(NOT_ALLOWED_EMAIL_DOMAINS)):
            raise serializers.ValidationError("Email domain is not allowed.")

        existing_user = User.objects.filter(email=email)
    
        if existing_user.exists():
            raise serializers.ValidationError("Email already exists.")

        return email

    # Validate password
    def validate(self, attrs):
        password1 = attrs.get('password1')
        password2 = attrs.get('password2')

        if not password1 or not password2:
            raise serializers.ValidationError({"password2": "Both password fields are required."})

        if password1 != password2:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        
        return attrs

    # Create user
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password1']
        )

        # Get the Request
        request = self.context.get('request')

        # Send Verification Email
        setup_user_email(request, user, [])

        return user
