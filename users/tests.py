from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User


class UserTestCase(APITestCase):
    """ Тестирование для User """
    def setUp(self) -> None:
        # пользователи для теста
        self.user1 = User.objects.create(
            phone='+79525552233', invite_code='x1X2cv', is_active=True, is_authenticate=True
        )
        self.user2 = User.objects.create(
            phone='+79525552234', invite_code='1q2SDe', is_active=True, is_authenticate=True
        )
        # модератор для теста
        self.moder = User.objects.create(
            phone='+79525555555', is_staff=True, is_active=True, is_authenticate=True
        )

    def test_auth_user(self):
        """ Тест для авторизации пользователя """
        data_post = {
            'phone': '+79531112244'
        }
        response = self.client.post('/api/users/login/', data=data_post)
        self.assertEquals(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertEquals(
            response.json(),
            {'message': 'На указанный Вами номер телефона отправлено SMS с кодом доступа.',
             'test_code': response.json()['test_code']}
        )

        data_put = {
            'auth_code': response.json()['test_code']
        }
        response_put = self.client.put('/api/users/login/', data=data_put)
        self.assertEquals(
            response_put.status_code,
            status.HTTP_200_OK
        )
        self.assertEquals(
            response_put.json(),
            {'message': 'Доступ разрешен.'}
        )

    def test_errors_auth_user(self):
        """ Тест для проверки ошибок авторизации пользователя """
        # номер начинается не на +7
        data_post = {
            'phone': '+19531112244'
        }
        response = self.client.post('/api/users/login/', data=data_post)
        self.assertEquals(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEquals(
            response.json(),
            {'message': 'Не верный запрос.'}
        )

        # пустое поле
        data_post2 = {
            'phone': ''
        }
        response2 = self.client.post('/api/users/login/', data=data_post2)
        self.assertEquals(
            response2.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEquals(
            response2.json(),
            {'message': 'Не верный запрос.'}
        )

    def test_get_profile_user(self):
        """ Тест для проверки отображения профиля пользователя """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/users/{self.user1.id}/')
        self.assertEquals(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEquals(
            response.json(),
            {'phone': '+79525552233', 'email': None, 'avatar': None, 'city': None, 'telegram_id': None,
             'invite_code': 'x1X2cv', 'referral_code': None, 'all_referrals': []}
        )

    def test_update_user(self):
        """ Тест для обновления профиля пользователя """
        self.client.force_authenticate(user=self.user1)
        data = {
            'phone': self.user1.phone,
            'city': 'test_city'
        }
        response = self.client.put(f'/api/users/{self.user1.id}/', data=data)
        self.assertEquals(
            response.json(),
            {'phone': '+79525552233', 'email': None, 'avatar': None, 'city': 'test_city', 'telegram_id': None,
             'invite_code': 'x1X2cv', 'referral_code': None, 'all_referrals': []}
        )

    def test_invite_code(self):
        """ Тест на использование Invite кода """
        self.client.force_authenticate(user=self.user2)
        data = {
            'phone': self.user2.phone,
            'referral_code': self.user1.invite_code
        }
        response = self.client.put(f'/api/users/{self.user2.id}/', data=data)
        self.assertEquals(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEquals(
            response.json(),
            {'phone': '+79525552234', 'email': None, 'avatar': None, 'city': None, 'telegram_id': None,
             'invite_code': '1q2SDe', 'referral_code': 'x1X2cv', 'all_referrals': []}
        )
        response_error1 = self.client.put(f'/api/users/{self.user2.id}/', data=data)
        self.assertEquals(
            response_error1.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEquals(
            response_error1.json(),
            {'message': 'Вы уже использовали invite код.'}
        )
        data2 = {
            'phone': self.user2.phone,
            'referral_code': 'X25dcv'
        }
        response_error2 = self.client.put(f'/api/users/{self.user2.id}/', data=data2)
        self.assertEquals(
            response_error2.status_code,
            status.HTTP_404_NOT_FOUND
        )
        self.assertEquals(
            response_error2.json(),
            {'message': 'Не верный invite код.'}
        )

    def test_user_profile_with_referrals(self):
        """ Тест на отображение рефералов в профиле пользователя """
        self.client.force_authenticate(user=self.user2)
        data = {
            'phone': self.user2.phone,
            'referral_code': self.user1.invite_code
        }
        response = self.client.put(f'/api/users/{self.user2.id}/', data=data)
        self.client.force_authenticate(user=self.user1)
        response_get = self.client.get(f'/api/users/{self.user1.id}/')
        self.assertEquals(
            response_get.status_code,
            status.HTTP_200_OK
        )
        self.assertEquals(
            response_get.json(),
            {'phone': '+79525552233', 'email': None, 'avatar': None, 'city': None, 'telegram_id': None,
             'invite_code': 'x1X2cv', 'referral_code': None,
             'all_referrals': [{'phone': '+79525552234', 'city': None, 'telegram_id': None, 'email': None}]}
        )

    def test_list_users_for_staff(self):
        """ Тест на получение списка пользователей модератором """
        self.client.force_authenticate(user=self.moder)
        response = self.client.get('/api/users/list/')
        self.assertEquals(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEquals(
            response.json(),
            [{'pk': self.user1.id, 'phone': '+79525552233', 'city': None, 'telegram_id': None, 'email': None,
              'is_active': True, 'is_authenticate': True},
             {'pk': self.user2.id, 'phone': '+79525552234', 'city': None, 'telegram_id': None, 'email': None,
              'is_active': True, 'is_authenticate': True},
             {'pk': self.moder.id, 'phone': '+79525555555', 'city': None, 'telegram_id': None, 'email': None,
              'is_active': True, 'is_authenticate': True}]
        )

    def test_delete_user(self):
        """ Тест на удаление пользователя """
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f'/api/users/{self.user2.id}/')
        self.assertEquals(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        # удаление пользователя модератором
        self.client.force_authenticate(user=self.moder)
        response = self.client.delete(f'/api/users/{self.user1.id}/')
        self.assertEquals(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )
