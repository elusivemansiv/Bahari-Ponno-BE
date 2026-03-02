from rest_framework import serializers
from .models import User, CustomerProfile

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['address', 'facebook_profile']

class UserSerializer(serializers.ModelSerializer):
    customer_profile = CustomerProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'role', 'password', 'customer_profile']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('customer_profile', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        if user.role == 'ADMIN':
            user.is_staff = True
            user.is_superuser = True
        elif user.role == 'STAFF':
            user.is_staff = True
        user.save()

        if profile_data:
            CustomerProfile.objects.create(user=user, **profile_data)
        elif user.role == 'CUSTOMER':
            CustomerProfile.objects.create(user=user)

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('customer_profile', None)
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if profile_data and hasattr(instance, 'customer_profile'):
            profile = instance.customer_profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance
