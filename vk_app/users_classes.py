import requests
import time
import string
from datetime import datetime
from pprint import pprint


TOKEN = '643664a007e9e890893d3fb5c109d24a0b6ad0ff9c17d9daf529b278f0a8d213d8a7462b75c20a1cdebb0'
V = '5.92'


class VKuser:
    bdate = None
    city = None
    sex = None
    age = None
    interests = set()
    books = set()
    groups_ = set()
    friends_ = set()

    def __init__(self, vk_id):
        if str(vk_id).isdigit():
            self.vk_id = vk_id
        else:
            params = {
                'user_id': vk_id,
                'access_token': TOKEN,
                'v': V
            }
            response = requests.get('https://api.vk.com/method/users.get', params)
            user_profile = response.json()
            self.vk_id = str(user_profile['response'][0]['id'])

    def select_user_info(self):
        params = {
            'user_id': self.vk_id,
            'fields': 'id,first_name,last_name,bdate,books,city,common_count,country,interests,photo_max_orig,sex',
            'access_token': TOKEN,
            'v': V
        }
        response = requests.get('https://api.vk.com/method/users.get', params)
        user_info = response.json()

        try:
            if 'bdate' in user_info['response'][0]:
                try:
                    bdate = datetime.strptime(user_info['response'][0]['bdate'], '%d.%m.%Y').date()
                    self.bdate = bdate
                    age = datetime.today().year - bdate.year \
                          - ((datetime.today().month, datetime.today().day)
                             < (bdate.month, bdate.day))
                    self.age = age
                except ValueError:
                    self.bdate = self.bdate
                    self.age = self.age

            if 'city' in user_info['response'][0]:
                self.city = int(user_info['response'][0]['city']['id'])

            if 'sex' in user_info['response'][0]:
                self.sex = int(user_info['response'][0]['sex'])

            if 'interests' in user_info['response'][0]:
                interests = user_info['response'][0]['interests']
                interests = ''.join(l for l in interests if l not in string.punctuation)
                self.interests = set(interests.lower().split())

        except KeyError:
            pass

        time.sleep(0.3)
        return user_info

    def friends(self):
        params = {
            'user_id': self.vk_id,
            'access_token': TOKEN,
            'v': V,
            'fields': 'domain'
        }
        response = requests.get('https://api.vk.com/method/friends.get', params)
        friends_info = response.json()

        friends_set = set()
        try:
            for friend in friends_info['response']['items']:
                friends_set.add(friend['id'])
            self.friends_ = friends_set
        except KeyError:
            self.friends_ = set()
        return friends_set

    def groups(self):
        params = {
            'user_id': self.vk_id,
            'extended': '1',
            'access_token': TOKEN,
            'v': '5.92',
            'fields': 'members_count'
        }
        try:
            response = requests.get('https://api.vk.com/method/groups.get', params)
            groups_info = response.json()
            groups_set = set()
            for group in groups_info['response']['items']:
                groups_set.add(group['id'])
            return groups_set
        except KeyError:
            return set()

    def photos(self):
        params = {
            'owner_id': self.vk_id,
            'album_id': 'profile',
            'extended': '1',
            'access_token': TOKEN,
            'v': V
        }
        response = requests.get('https://api.vk.com/method/photos.get', params)
        owner_photos = response.json()
        try:
            photos_dict = dict()
            for photo in owner_photos['response']['items']:
                likes = photo['likes']['count']
                for size in photo['sizes']:
                    if size['type'] == 'x':
                        link = size['url']
                photos_dict[link] = likes

            top3_photos = sorted(photos_dict.items(),
                                 key=lambda x: x[1],
                                 reverse=True)[0:3]
            time.sleep(0.3)
            return top3_photos
        except KeyError:
            return list()


class MainUser(VKuser):
    friends_weight = 0.3
    age_weight = 0.25
    groups_weight = 0.2
    interests_weight = 0.15
    books_weight = 0.1
    select_users = list()

    def compare_user_with(self, other):
        user_ratings = []
        if self.age is not None and other.age is not None:
            age_dif = self.age - other.age
            if abs(age_dif) == 0:
                user_ratings.append(4 * self.age_weight)
            elif abs(age_dif) == 1:
                user_ratings.append(3 * self.age_weight)
            elif abs(age_dif) == 2:
                user_ratings.append(2 * self.age_weight)
            else:
                user_ratings.append(1 * self.age_weight)
        else:
            user_ratings.append(0)

        common_friends = self.friends_ & other.friends_
        if len(common_friends) > 20:
            user_ratings.append(4 * self.friends_weight)
        elif 15 < len(common_friends) <= 20:
            user_ratings.append(3 * self.friends_weight)
        elif 10 < len(common_friends) <= 15:
            user_ratings.append(2 * self.friends_weight)
        elif 0 < len(common_friends) <= 10:
            user_ratings.append(1 * self.friends_weight)
        else:
            user_ratings.append(0 * self.friends_weight)

        common_groups = self.groups_ & other.groups_
        if len(common_groups) > 20:
            user_ratings.append(4 * self.groups_weight)
        elif 15 < len(common_groups) <= 20:
            user_ratings.append(3 * self.groups_weight)
        elif 10 < len(common_groups) <= 15:
            user_ratings.append(2 * self.groups_weight)
        elif 0 < len(common_groups) <= 10:
            user_ratings.append(1 * self.groups_weight)
        else:
            user_ratings.append(0 * self.groups_weight)

        common_interests = self.interests & other.interests
        if len(common_interests) != 0:
            user_ratings.append(4 * self.interests_weight)
        else:
            user_ratings.append(0 * self.interests_weight)

        common_books = self.books & other.books
        if len(common_books) != 0:
            user_ratings.append(4 * self.books_weight)
        else:
            user_ratings.append(0 * self.books_weight)

        return sum(user_ratings)

    def select_users_search(self):
        if self.sex == 2:
            sex = '1'
        else:
            sex = '2'
        if self.age is not None:
            age_from = str(self.age - 3)
            age_to = str(self.age + 3)
        else:
            age_from = str(0)
            age_to = str(50)
        params = {
            'count': '50',
            'fields': 'id,first_name,last_name,about,bdate,books,city,'
                      'common_count,country,interests,photo_max_orig,sex',
            'access_token': TOKEN,
            'v': V,
            'city': str(self.city),
            'sex': sex,
            'age_from': age_from,
            'age_to': age_to,
            'has_photo': '1'
        }
        response = requests.get('https://api.vk.com/method/users.search', params)
        select_users_data = response.json()

        select_users_list = []
        for user in select_users_data['response']['items']:
            select_users_list.append(user['id'])

        self.select_users = select_users_list
        return select_users_list


if __name__ == "__main__":
    User = VKuser('43782857')
    User.groups()
    User.friends()
    pprint(User.select_user_info())
    pprint(User.__dict__)