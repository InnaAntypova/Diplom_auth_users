from rest_framework import serializers
from users.models import User
from users.validators import PhoneNumberValidator


class UserRegistrationSerializer(serializers.ModelSerializer):
    """ Сериализатор для регистрации пользователя """
    validators = [PhoneNumberValidator()]

    class Meta:
        model = User
        fields = ['phone']


class UserVerifySerializer(serializers.ModelSerializer):
    """ Сериализатор для верификации пользователя """
    class Meta:
        model = User
        fields = ['auth_code']


class UserReferralSerializer(serializers.ModelSerializer):
    """ Сериализатор для отображения реферрала """
    class Meta:
        model = User
        fields = ['phone', 'city', 'telegram_id', 'email']


class UserProfileSerializer(serializers.ModelSerializer):
    """ Сериализатор для отображения профиля пользователя """
    all_referrals = serializers.SerializerMethodField()

    def get_all_referrals(self, instance):
        """ Метод для получения информации об реферралах """
        return UserReferralSerializer(User.objects.filter(referrals=instance.pk), many=True).data

    class Meta:
        model = User
        fields = ['phone', 'email', 'avatar', 'city', 'telegram_id', 'invite_code', 'referral_code', 'all_referrals']


class UserStaffSerializer(serializers.ModelSerializer):
    """ Сериализатор для отображения пользователей для модератора """
    class Meta:
        model = User
        fields = ['pk', 'phone', 'city', 'telegram_id', 'email', 'is_active', 'is_authenticate']
