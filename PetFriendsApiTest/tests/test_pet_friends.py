from api import PetFriends
from settings import valid_password, valid_email, no_valid_email, no_valid_password
import os

pf = PetFriends()


class TestException(Exception):
    pass


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert "key" in result


def test_get_all_pets_with_valid_key(filter="my_pets"):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result["pets"]) > 0


def test_add_new_pet_with_valid_data(name='Маркиз', animal_type='Русская голубая', age='2',
                                     pet_photo='images/Russkaya-golubaya-koshka-65.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_add_new_pet_without_photo(name='Mars', animal_type='cat', age='2'):
    """Добавление нового питомца в систему с без фото"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.post_add_new_pet_without_photo(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name


def test_add_photo_of_a_pet(pet_photo='images/Russkaya-golubaya-koshka-65.jpg'):
    """Добавление фото к существующей анкете питомца"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) == 0:
        pf.post_add_new_pet_without_photo(auth_key, "", "", "")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_id = my_pets['pets'][0]['id']
    status, result = pf.post_add_photo_of_a_pet(auth_key, pet_id, pet_photo)

    assert status == 200
    assert result['pet_photo']


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Маркиз", "кот", "2", "images/Russkaya-golubaya-koshka-65")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Кот', age=1):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_get_api_key_for_valid_user_negative(email=no_valid_email, password=no_valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    print("The error code means that provided combination of user email and password is incorrect")


def test_get_api_key_password_is_none(email=valid_email, password=""):
    """Вход в систему без ввода пароля"""

    status, result = pf.get_api_key(email, password)
    assert status == 403
    print("The error code means that provided combination of user email and password is incorrect")


def test_get_api_key_emel_is_none(email="", password=valid_password):
    """Вход в систему без ввода логина"""

    status, result = pf.get_api_key(email, password)
    assert status == 403
    print("The error code means that provided combination of user email and password is incorrect")


def test_get_all_pets_with_valid_key_negative(filter=""):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    auth_key["key"] = auth_key["key"] + "223"
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 403
    print("The error code means that provided auth_key is incorrect")


def test_add_new_pet_without_photo_negative(name='', animal_type='', age=''):
    """Добавление нового питомца в систему  без фото и без параметров"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.post_add_new_pet_without_photo(auth_key, name, animal_type, age)
    assert status == 400
    print("The error code means that provided data is incorrect")


def test_add_new_pet_with_negative_data(name='', animal_type='', age='',
                                        pet_photo='images/Russkaya-golubaya-koshka-65.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 400
    print("The error code means that provided data is incorrect")



def test_successful_update_self_pet_info_negative(name='', animal_type='', age= int ):
    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 403
        print("	The error code means that provided data is incorrect")
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise TestException("There is no my pets")



def test_successful_delete_self_pet_negative():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Маркиз", "кот", "2", 'images/Russkaya-golubaya-koshka-65.jpg')
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    print(pet_id)
    pet_id = pet_id + "323"
    print(pet_id)

    status, _ = pf.delete_pet(auth_key, pet_id)

    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")


    assert status == 200
    print("Удалён несущестыующий петомец")


