import json
from typing import Dict, Type, Set, Any
from pygame import Rect
from game.objects.entities.entity import Entity
from game.objects.entities.player.player import Player
from game.objects.system_objects.camera import Camera
from game.objects.entities.enemy.zombie.zombie import Zombie
from game.objects.envirements.ground.ground import Ground
from game.objects.items.weapons.weapon import Weapon
from game.objects.items.weapons.shotgun.shotgun import Shotgun
from game.objects.items.weapons.poison_gun.poison_gun import PoisonGun
from game.core.storage import storage

CLASS_REGISTRY: Dict[str, Type] = {
    'Entity': Entity,
    'Player': Player,
    'Zombie': Zombie,
    'Ground': Ground,
    'Weapon': Weapon,
    'Shotgun': Shotgun,
    'Camera': Camera,
    'PoisonGun': PoisonGun
}


def serialize_rect(rect: Rect) -> dict:
    """Сериализует Rect в словарь"""
    return {
        '__class__': 'Rect',
        'x': rect.x,
        'y': rect.y,
        'width': rect.width,
        'height': rect.height
    }


def serialize_obj(obj, _seen: Set[int] = None) -> dict:
    if _seen is None:
        _seen = set()

    if obj is None:
        return None

    obj_id = id(obj)
    if obj_id in _seen:
        return {"__ref__": obj_id}
    _seen.add(obj_id)

    result = {
        "__class__": obj.__class__.__name__,
        "__id__": obj_id,
    }

    attributes = {}
    for key, value in obj.__dict__.items():
        # Пропускаем приватные атрибуты и ненужные ссылки
        if key.startswith('_') and key not in ('_x', '_y', '_width', '_height'):
            continue

        # Сохраняем ссылку на target
        if key == 'target' and value is not None:
            attributes[key] = {"__ref__": id(value)}
            continue

        # Преобразуем _атрибуты в обычные (убираем _ в начале)
        clean_key = key[1:] if key.startswith('_') else key

        # Сериализация в зависимости от типа
        if isinstance(value, Rect):
            attributes[clean_key] = serialize_rect(value)
        elif hasattr(value, '__dict__'):
            attributes[clean_key] = serialize_obj(value, _seen)
        elif isinstance(value, (list, tuple, set)):
            attributes[clean_key] = [
                serialize_obj(item, _seen) if hasattr(item, '__dict__') or isinstance(item, Rect) else item
                for item in value
            ]
        else:
            # Базовые типы (int, float, str, bool и т.д.)
            try:
                json.dumps(value)  # Проверяем сериализуемость
                attributes[clean_key] = value
            except TypeError:
                continue  # Пропускаем несериализуемые атрибуты

    result['attributes'] = attributes
    return result


def save_level(filename: str):
    """Сохраняет уровень в файл"""
    level_data = {
        'entities': [serialize_obj(entity) for entity in storage.entities],
        'grounds': [serialize_obj(ground) for ground in storage.grounds],
        'camera': serialize_obj(storage.camera),
    }

    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(level_data, file, ensure_ascii=False, indent=4)


def create_objects_from_json(json_data: Dict[str, Any]) -> None:
    """
    Создает объекты из JSON данных с учетом вложенности и регистрации классов.
    """
    # Словарь для хранения созданных объектов по их ID
    created_objects: Dict[int, Any] = {}

    def create_object(obj_data: Dict[str, Any]) -> Any:
        # Если объект уже создан, возвращаем его
        obj_id = obj_data.get('__id__')
        if obj_id in created_objects:
            return created_objects[obj_id]

        class_name = obj_data.get('__class__')
        if class_name not in CLASS_REGISTRY:
            return None

        cls = CLASS_REGISTRY[class_name]
        attributes = obj_data.get('attributes', {})

        # Обрабатываем ссылки на другие объекты
        processed_attrs = {}
        for key, value in attributes.items():
            if isinstance(value, dict):
                if '__ref__' in value:
                    # Это ссылка на другой объект
                    ref_id = value['__ref__']
                    if ref_id in created_objects:
                        processed_attrs[key] = created_objects[ref_id]
                    else:
                        # Пока не можем обработать, оставляем как есть
                        processed_attrs[key] = value
                elif '__class__' in value:
                    # Это вложенный объект
                    processed_attrs[key] = create_object(value)
                else:
                    processed_attrs[key] = value
            else:
                processed_attrs[key] = value

        # Создаем объект
        obj = cls(**processed_attrs)

        # Сохраняем созданный объект
        if obj_id is not None:
            created_objects[obj_id] = obj

        return obj

    for items_data in json_data.get('items', []):
        create_object(items_data)

    # Обрабатываем все сущности
    for entity_data in json_data.get('entities', []):
        create_object(entity_data)

    # Обрабатываем все земли
    for ground_data in json_data.get('grounds', []):
        create_object(ground_data)

    # Обрабатываем камеру
    if 'camera' in json_data and json_data['camera']:
        create_object(json_data['camera'])

    # Обрабатываем игровые опции (если нужно)
    if 'game_options' in json_data:
        # Здесь может быть дополнительная логика для обработки game_options
        pass


def load_level(filename: str):
    """Загружает уровень из файла"""
    with open(filename, 'r', encoding='utf-8') as file:
        level_data = json.load(file)

    # Очищаем текущее состояние
    storage.entities.clear()
    storage.grounds.clear()
    storage.items.clear()
    storage.shots.clear()

    create_objects_from_json(level_data)
