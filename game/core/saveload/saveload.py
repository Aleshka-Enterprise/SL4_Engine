import inspect
import json
from typing import Dict, Type, Set, Any, get_type_hints
from pygame import Rect
from game import settings
from game.models.entities.entity import Entity
from game.models.entities.player.player import Player
from game.models.system_objects.camera import Camera
from game.models.entities.enemy.zombie.zombie import Zombie
from game.models.envirements.ground.ground import Ground
from game.models.items.weapons.weapon import Weapon
from game.models.items.weapons.shotgun.shotgun import Shotgun
from game.models.items.weapons.poison_gun.poison_gun import PoisonGun
from game.core.storage import storage

CLASS_REGISTRY: Dict[str, Type] = {
    'Entity': Entity,
    'Player': Player,
    'Zombie': Zombie,
    'Ground': Ground,
    'Weapon': Weapon,
    'Shotgun': Shotgun,
    'Camera': Camera,
    'PoisonGun': PoisonGun,
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
    storage.grounds.clear()
    storage.items.clear()

    create_objects_from_json(level_data)


def generate_ai_documentation(registry):
    """Генерирует документацию для ИИ в понятном формате"""
    docs = {
        'version': '1.0',
        'classes': {}
    }
    
    for class_name, cls in registry.items():
        class_doc = {
            'description': cls.__doc__ or f'Class {class_name}',
            'parent': [base.__name__ for base in cls.__bases__ if base != object],
            'init_parameters': {},
            'attributes': {},
            'required_attributes': [],
            'optional_attributes': []
        }
        
        # Получаем параметры __init__
        init_sig = inspect.signature(cls.__init__)
        for param_name, param in init_sig.parameters.items():
            if param_name == 'self':
                continue
                
            param_info = {
                'type': get_type_hints(cls.__init__).get(param_name, 'Any'),
                'required': param.default == inspect.Parameter.empty,
                'default': None if param.default == inspect.Parameter.empty else param.default
            }
            
            if param_info['required']:
                class_doc['required_attributes'].append(param_name)
            else:
                class_doc['optional_attributes'].append(param_name)
                
            class_doc['init_parameters'][param_name] = param_info
        
        # Пытаемся создать экземпляр и посмотреть атрибуты
        try:
            # Создаем с минимальными параметрами
            minimal_params = {}
            for param_name, param_info in class_doc['init_parameters'].items():
                if param_info['required']:
                    # Для обязательных параметров пробуем угадать значение
                    if 'x' in param_name or 'y' in param_name:
                        minimal_params[param_name] = 0
                    elif 'width' in param_name or 'height' in param_name:
                        minimal_params[param_name] = 50
                    elif 'color' in param_name:
                        minimal_params[param_name] = [0, 0, 0]
                    else:
                        minimal_params[param_name] = None
            
            if minimal_params:
                obj = cls(**minimal_params)
            else:
                obj = cls()
            
            # Собираем все атрибуты
            for attr_name, attr_value in obj.__dict__.items():
                clean_name = attr_name.lstrip('_')
                class_doc['attributes'][clean_name] = {
                    'type': type(attr_value).__name__,
                    'example': attr_value if isinstance(attr_value, (int, float, str, bool, list)) else str(attr_value),
                    'is_object': hasattr(attr_value, '__dict__')
                }
        except Exception as e:
            class_doc['error'] = str(e)
        
        docs['classes'][class_name] = class_doc
    
    return docs

if settings.DEBUG and False:
    # TODO починить генератор документации
    docs = generate_ai_documentation(CLASS_REGISTRY)
    with open('level_docs.json', 'w', encoding='utf-8') as f:
        json.dump(docs, f, ensure_ascii=False, indent=2, default=str)
