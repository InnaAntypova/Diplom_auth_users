import time
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsUserStaff, IsOwner
from users.services import generate_auth_code, generate_invite_code
from rest_framework import status, generics
from users.models import User
from users.serializers import UserRegistrationSerializer, UserVerifySerializer, UserProfileSerializer, \
    UserStaffSerializer


class UserAuthAPIView(APIView):
    """ Представление для авторизации пользователя """
    serializer_class = UserRegistrationSerializer

    @swagger_auto_schema(
        request_body=UserRegistrationSerializer
    )
    def post(self, request, *args, **kwargs):
        """ Метод для отправки на сервер номера телефона и получения кода авторизации """
        serializer = UserRegistrationSerializer(data=request.data)
        message = f'На указанный Вами номер телефона отправлено SMS с кодом доступа.'
        try:
            if serializer.is_valid():
                # пользователь отсутствует в базе
                new_user = User.objects.create(phone=serializer.validated_data['phone'])
                new_user.auth_code = generate_auth_code()
                new_user.invite_code = generate_invite_code()
                new_user.set_password(new_user.auth_code)  # из кода аутентификации сделать пароль
                new_user.save()
                time.sleep(2)
                # здесь вставить отправку кода на телефон
                return Response({'message': message, 'test_code': new_user.auth_code}, status=status.HTTP_201_CREATED)
            else:
                # пользователь есть в базе
                user = User.objects.get(phone=serializer.data['phone'])
                user.auth_code = generate_auth_code()  # обновить код доступа
                user.set_password(user.auth_code)  # обновить пароль из нового кода доступа
                user.save()
                time.sleep(2)
                # здесь вставить отправку кода на телефон
                return Response({'message': message, 'test_code': user.auth_code}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'Не верный запрос.'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=UserVerifySerializer
    )
    def put(self, request, *args, **kwargs):
        """ Метод для отправки на сервер полученного кода авторизации """
        serializer = UserVerifySerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['auth_code']
            user = User.objects.filter(auth_code=code)
            # если пользователь с таким кодом есть --> активировать и аутентифицировать
            if user:
                user.update(is_active=True, is_authenticate=True)
                return Response({'message': 'Доступ разрешен.'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Доступ запрещен. Не верный код.'}, status=status.HTTP_403_FORBIDDEN)


class UserProfileUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    """ Представление для получения и обновления профиля пользователя """
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsOwner | IsUserStaff]

    def update(self, request, *args, **kwargs):
        """ Метод для обновления профиля пользователя """
        data = request.data
        if 'referral_code' not in data:
            return super(UserProfileUpdateDeleteAPIView, self).update(request, *args, **kwargs)
        else:
            try:
                referral_user = User.objects.get(invite_code=data['referral_code'])  # тот, кто привел
                current_user = User.objects.get(id=request.user.id)  # текущий пользователь
                if current_user.referrals:
                    return Response({'message': 'Вы уже использовали invite код.'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    current_user.referrals = referral_user  # добавить реферала
                    current_user.referral_code = data['referral_code']
                    current_user.save()
                    return super(UserProfileUpdateDeleteAPIView, self).update(request, *args, **kwargs)
            except User.DoesNotExist:
                return Response({'message': 'Не верный invite код.'}, status=status.HTTP_404_NOT_FOUND)


class UserListAPIView(generics.ListAPIView):
    """ Представление для отображения списка пользователей для модератора """
    serializer_class = UserStaffSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsUserStaff]
