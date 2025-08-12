from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from . import views
from .models import DroneCategory, Pilot


class DroneCategoryTests(APITestCase):
    def post_drone_category(self, name):
        url = reverse(f'v1:{views.DroneCategoryList.name}')
        data = {'name': name}
        response = self.client.post(url, data=data, format='json')
        return response

    def test_post_and_get_drone_category(self):
        """
        Ensure we can create a new DroneCategory and then retrieve it
        :return: None
        """
        new_drone_category_name = 'Hexacopter'
        response = self.post_drone_category(new_drone_category_name)
        print("\nPK {0}\n".format(DroneCategory.objects.get().pk))
        assert response.status_code == status.HTTP_201_CREATED
        assert DroneCategory.objects.count() == 1
        assert DroneCategory.objects.get().name == new_drone_category_name

    def test_post_existing_drone_category_name(self):
        """
        Ensure we cannot create a DroneCategory with an existing name
        :return: None
        """
        new_drone_category_name = 'Duplicated copter'
        response1 = self.post_drone_category(new_drone_category_name)
        assert response1.status_code == status.HTTP_201_CREATED
        response2 = self.post_drone_category(new_drone_category_name)
        print(response2)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_filter_drone_category_by_name(self):
        """
        Ensure we can filter a drone category by name
        :return: None
        """
        drone_category_name1 = 'Hexacopter'
        self.post_drone_category(drone_category_name1)
        drone_category_name2 = 'Octocopter'
        self.post_drone_category(drone_category_name2)
        filter_by_name = {'name': drone_category_name1}
        url = f'{reverse(f"v1:{views.DroneCategoryList.name}")}?{urlencode(filter_by_name)}'
        print(url)
        response = self.client.get(url, format='json')
        print(response, response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['name'] == drone_category_name1

    def test_get_drone_categories_collection(self):
        """
        Ensure we can retrieve the drone categories collection
        :return: None
        """
        new_drone_category_name = 'Super Copter'
        self.post_drone_category(new_drone_category_name)
        url = reverse(f'v1:{views.DroneCategoryList.name}')
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['name'] == new_drone_category_name

    def test_update_drone_category(self):
        """
        Ensure we can update a single field for a drone category
        :return: None
        """
        drone_category_name = 'Category Initial Name'
        response = self.post_drone_category(drone_category_name)
        url = reverse(f'v1:{views.DroneCategoryDetail.name}', args=({response.data['pk']}))
        updated_category_name = 'Updated name'
        data = {'name': updated_category_name}
        patch_response = self.client.patch(url, data=data, format='json')
        assert patch_response.status_code == status.HTTP_200_OK
        assert patch_response.data['name'] == updated_category_name

    def test_get_drone_category(self):
        """
        Ensure we can get a single drone category by id
        :return: None
        """
        drone_category_name = 'Easy to retrieve'
        response = self.post_drone_category(drone_category_name)
        url = reverse(f'v1:{views.DroneCategoryDetail.name}', args=({response.data['pk']}))
        get_response = self.client.get(url, format='json')
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.data['name'] == drone_category_name


class PilotTests(APITestCase):
    def post_pilot(self, name, gender, races_count):
        url = reverse(f'v1:{views.PilotList.name}')
        print('\n' + url)
        data = {
            'name': name,
            'gender': gender,
            'races_count': races_count}
        response = self.client.post(url, data=data, format='json')
        return response

    def create_user_and_set_token_credentials(self):
        user = User.objects.create_user('user01', 'user01.example@gmail.com', '1234')
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

    def test_post_and_get_pilot(self):
        """
        Ensure we can create a new pilot and then retrieve it
        Ensure we cannot retrieve the persisted pilot without token
        :return: None
        """
        self.create_user_and_set_token_credentials()
        new_pilot_name = 'Timur'
        new_pilot_gender = Pilot.MALE
        new_pilot_races_count = 5
        response = self.post_pilot(new_pilot_name, new_pilot_gender, new_pilot_races_count)
        print(f'\n{Pilot.objects.get().pk}\n')
        assert response.status_code == status.HTTP_201_CREATED
        assert Pilot.objects.count() == 1

        saved_pilot = Pilot.objects.get()
        assert saved_pilot.name == new_pilot_name
        assert saved_pilot.gender == new_pilot_gender
        assert saved_pilot.races_count == new_pilot_races_count

        url = reverse(f'v1:{views.PilotDetail.name}', args=({saved_pilot.pk}))
        authorized_get_response = self.client.get(url, format='json')
        assert authorized_get_response.status_code == status.HTTP_200_OK
        assert authorized_get_response.data['name'] == new_pilot_name

        # Clean up credentials
        self.client.credentials()
        unauthorized_get_response = self.client.get(url, format='json')
        assert unauthorized_get_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_try_to_post_pilot_without_token(self):
        """
        Ensure we cannot create a pilot without token
        :return: None
        """
        new_pilot_name = 'Unauthorized pilot'
        new_pilot_gender = Pilot.MALE
        new_pilot_races_count = 5
        response = self.post_pilot(new_pilot_name,
                                   new_pilot_gender,
                                   new_pilot_races_count)
        print(response)
        print(Pilot.objects.count())
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Pilot.objects.count() == 0
