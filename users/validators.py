from rest_framework import serializers


class PhoneNumberValidator:
    """ Валидация заполнения поля для номера телефона """
    def __call__(self, value):
        phone = value.get('phone')
        if not phone:
            raise serializers.ValidationError('Номер телефона не может быть пуст.')
        else:
            if not phone.startswith('+7'):
                raise serializers.ValidationError('Номер телефона должен начинаться с +7...')
