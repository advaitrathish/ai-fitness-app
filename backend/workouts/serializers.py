from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


# ============================
# REGISTER SERIALIZER
# ============================

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    age = serializers.IntegerField()
    height = serializers.FloatField()
    weight = serializers.FloatField()
    goal = serializers.CharField()
    consent = serializers.BooleanField()

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "confirm_password",
            "age",
            "height",
            "weight",
            "goal",
            "consent",
        )

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")

        if not data["consent"]:
            raise serializers.ValidationError("Consent is required")

        return data

    def create(self, validated_data):
        age = validated_data.pop("age")
        height = validated_data.pop("height")
        weight = validated_data.pop("weight")
        goal = validated_data.pop("goal")
        consent = validated_data.pop("consent")
        validated_data.pop("confirm_password")

        user = User.objects.create_user(**validated_data)

        profile = user.profile
        profile.age = age
        profile.height = height
        profile.weight = weight
        profile.goal = goal
        profile.consent = consent
        profile.save()

        return user


# ============================
# CURRENT USER SERIALIZER
# ============================

class MeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")

    class Meta:
        model = UserProfile
        fields = (
            "username",
            "xp",
            "level",
            "total_workouts",
            "age",
            "height",
            "weight",
            "goal",
        )