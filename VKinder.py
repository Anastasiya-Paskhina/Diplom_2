from vk_app.users_classes import VKuser, MainUser
from database.database import DataBase
from pprint import pprint


def top10(main_user):
    database = DataBase()
    select_users = main_user.select_users_search()
    select_users_dict = dict()
    select_users_photos = dict()
    for user in select_users:
        if database.check(user):
            other_user = VKuser(str(user))
            other_user.select_user_info()
            other_user.groups()
            other_user.friends()
            select_users_photos[user] = other_user.photos()
            select_users_dict[user] = main_user.compare_user_with(other_user)
            print('...')
        else:
            continue
    select_users_dict = sorted(select_users_dict.items(),
                                 key=lambda x: x[1],
                                 reverse=True)

    data_to_db = list()
    for user in select_users_dict[0:10]:
        top10_users_dict = dict()
        user_photos = select_users_photos[user[0]]
        photos_list = list()
        for photo in user_photos:
            photos_list.append(photo[0])

        top10_users_dict['user_id'] = user[0]
        top10_users_dict['user_page'] = 'https://vk.com/id' + str(user[0])
        top10_users_dict['photos'] = photos_list
        data_to_db.append(top10_users_dict)
    database.add(data_to_db)
    return data_to_db


if __name__ == "__main__":
    main_user = MainUser('43782857')
    main_user.select_user_info()
    main_user.groups()
    main_user.friends()
    top_10 = top10(main_user)
    pprint(top_10)