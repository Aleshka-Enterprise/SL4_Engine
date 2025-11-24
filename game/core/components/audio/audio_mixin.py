import inspect
import pygame
import os
import random
from typing import Optional, Dict, List, Tuple
from enum import Enum
from game.settings import DEBUG

class PlaybackMode(Enum):
    RANDOM = "random"
    SEQUENTIAL = "sequential" 
    LOOP = "loop"
    SINGLE = "single"

class AudioManager:
    """
    Менеджер для управления звуковыми эффектами с поддержкой папок и режимов воспроизведения
    """
    
    _instance = None
    _audio_cache: Dict[str, pygame.mixer.Sound] = {}
    _sound_groups_cache: Dict[str, Dict] = {}  # Кэш групп звуков по классам
    _initialized_classes: set = set()  # Отслеживаем инициализированные классы
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_sound(cls, file_path: str) -> Optional[pygame.mixer.Sound]:
        """Получает звук из кэша или загружает его"""
        if file_path not in cls._audio_cache:
            try:
                cls._audio_cache[file_path] = pygame.mixer.Sound(file_path)
            except (pygame.error, FileNotFoundError) as e:
                if DEBUG:
                    print(f"Ошибка загрузки звука {file_path}: {e}")
                return None
        return cls._audio_cache[file_path]
    
    @classmethod
    def preload_sounds(cls, directory: str) -> None:
        """Предзагружает все звуки из директории"""
        if not os.path.exists(directory):
            return
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.wav', '.ogg', '.mp3')):
                    file_path = os.path.join(root, file)
                    cls.get_sound(file_path)
    
    @classmethod
    def get_sound_groups_for_class(cls, class_obj, audio_base_path: str) -> Dict[str, 'SoundGroup']:
        """Возвращает группы звуков для класса (с кэшированием)"""
        class_name = f"{class_obj.__module__}.{class_obj.__name__}"
        
        if class_name not in cls._sound_groups_cache:
            # Создаем группы звуков для этого класса
            sound_groups = {}
            
            if os.path.exists(audio_base_path):
                for action_name in os.listdir(audio_base_path):
                    action_path = os.path.join(audio_base_path, action_name)
                    
                    if os.path.isdir(action_path):
                        sound_group = SoundGroup(action_path)
                        if sound_group.sound_files:
                            sound_groups[action_name] = sound_group
                            if DEBUG:
                                print(f"Загружена звуковая группа '{action_name}' для {class_name} с {len(sound_group.sound_files)} звуками")
            
            cls._sound_groups_cache[class_name] = sound_groups
            cls._initialized_classes.add(class_name)
        
        return cls._sound_groups_cache[class_name]

class SoundGroup:
    """
    Группа звуков для определенного действия (например, стрельбы)
    """
    
    def __init__(self, directory: str, mode: PlaybackMode = PlaybackMode.RANDOM):
        self.directory = directory
        self.mode = mode
        self.sound_files: List[str] = []
        self.current_index = 0
        self._discover_sounds()
    
    def _discover_sounds(self) -> None:
        """Обнаруживает звуковые файлы в директории"""
        if not os.path.exists(self.directory):
            if DEBUG:
                print(f"Директория звуков не найдена: {self.directory}")
            return
        
        for file in sorted(os.listdir(self.directory)):
            if file.endswith(('.wav', '.ogg', '.mp3')):
                file_path = os.path.join(self.directory, file)
                self.sound_files.append(file_path)
    
    def get_next_sound(self) -> Optional[pygame.mixer.Sound]:
        """Возвращает следующий звук согласно режиму воспроизведения"""
        if not self.sound_files:
            return None
        
        if self.mode == PlaybackMode.RANDOM:
            file_path = random.choice(self.sound_files)
        elif self.mode in (PlaybackMode.SEQUENTIAL, PlaybackMode.LOOP):
            file_path = self.sound_files[self.current_index]
            self.current_index += 1
            if self.current_index >= len(self.sound_files):
                self.current_index = 0 if self.mode == PlaybackMode.LOOP else len(self.sound_files) - 1
        elif self.mode == PlaybackMode.SINGLE:
            file_path = self.sound_files[0] if self.sound_files else None
        
        return AudioManager.get_sound(file_path) if file_path else None
    
    def get_specific_sound(self, index: int = 0) -> Optional[pygame.mixer.Sound]:
        """Возвращает конкретный звук по индексу"""
        if 0 <= index < len(self.sound_files):
            return AudioManager.get_sound(self.sound_files[index])
        return None

class AudioMixin:
    """
    Продвинутый миксин для управления звуками с поддержкой папок и режимов воспроизведения
    """
    
    # Настройки вариаций по умолчанию
    _default_variation_settings = {
        'enabled': True,
        'volume_range': (0.8, 1.2),
        'variation_chance': 1.0
    }
    
    # Настройки предотвращения наложения по умолчанию для разных групп
    _default_prevent_overlap_settings = {
        'move': True,      # Для звуков движения - предотвращать наложение
        'shoot': False,    # Для выстрелов - разрешить наложение
        'reload': True,    # Для перезарядки - предотвращать наложение
        'jump': True,      # Для прыжков - предотвращать наложение
        'hurt': False,     # Для получения урона - разрешить наложение (много ударов сразу)
    }
    
    def _init_audio_mixin(self):
        """Инициализация аудио компонента"""
        self._audio_volume: float = 1.0
        self._currently_playing: Dict[str, pygame.mixer.Channel] = {}
        self._variation_settings = self._default_variation_settings.copy()
        self._prevent_overlap_settings = self._default_prevent_overlap_settings.copy()
        
        # Получаем группы звуков из кэша (не создаем новые)
        self._sound_groups = self._get_cached_sound_groups()
    
    def _get_audio_base_path(self) -> str:
        """Возвращает базовый путь к аудио файлам для этого класса"""
        try:
            class_file = inspect.getfile(self.__class__)
            class_dir = os.path.dirname(class_file)
            return os.path.join(class_dir, 'audio')
        except (TypeError, OSError):
            return os.path.join('audio', self.__class__.__name__.lower())
    
    def _get_cached_sound_groups(self) -> Dict[str, SoundGroup]:
        """Получает группы звуков из кэша"""
        audio_base_path = self._get_audio_base_path()
        return AudioManager.get_sound_groups_for_class(self.__class__, audio_base_path)
    
    def _apply_variations(self, sound: pygame.mixer.Sound) -> pygame.mixer.Sound:
        """Применяет вариации громкости к звуку"""
        if not self._variation_settings['enabled']:
            return sound
        
        if random.random() > self._variation_settings['variation_chance']:
            return sound
        
        # Изменяем громкость
        vol_min, vol_max = self._variation_settings['volume_range']
        volume_variation = random.uniform(vol_min, vol_max)
        
        current_volume = sound.get_volume()
        sound.set_volume(min(1.0, current_volume * volume_variation))
        
        return sound
    
    def set_sound_group_variations(self, group_name: str, 
                                 volume_range: Tuple[float, float] = (0.1, 1.2),
                                 variation_chance: float = 1.0) -> None:
        """Настраивает вариации для группы звуков"""
        self._variation_settings['volume_range'] = volume_range
        self._variation_settings['variation_chance'] = variation_chance
    
    def set_prevent_overlap(self, group_name: str, prevent: bool) -> None:
        """Устанавливает настройку предотвращения наложения для конкретной группы"""
        self._prevent_overlap_settings[group_name] = prevent
    
    def set_global_prevent_overlap(self, prevent: bool) -> None:
        """Устанавливает глобальную настройку предотвращения наложения для всех групп"""
        for group_name in self._prevent_overlap_settings:
            self._prevent_overlap_settings[group_name] = prevent
    
    def _should_prevent_overlap(self, group_name: str, prevent_overlap: Optional[bool]) -> bool:
        """Определяет, нужно ли предотвращать наложение для данной группы"""
        if prevent_overlap is not None:
            return prevent_overlap
        return self._prevent_overlap_settings.get(group_name, False)
    
    def play_sound(self, group_name: str, volume: Optional[float] = None, 
                   loops: int = 0, fade_ms: int = 0, 
                   mode: Optional[PlaybackMode] = None,
                   specific_index: Optional[int] = None,
                   apply_variations: bool = True,
                   prevent_overlap: Optional[bool] = None) -> bool:
        """
        Проигрывает звук из указанной группы
        
        Args:
            group_name: Название группы звуков (папки)
            volume: Громкость (0.0 - 1.0)
            loops: Количество повторений (-1 для бесконечного)
            fade_ms: Плавное нарастание звука в миллисекундах
            mode: Режим воспроизведения (переопределяет настройки группы)
            specific_index: Конкретный индекс звука для воспроизведения
            apply_variations: Применять ли вариации громкости
            prevent_overlap: Предотвращать ли наложение звуков из этой группы
                           (None - использовать настройки по умолчанию)
        """
        if not hasattr(self, '_sound_groups'):
            self._init_audio_mixin()
        
        if group_name not in self._sound_groups:
            if DEBUG:
                print(f"Звуковая группа '{group_name}' не найдена. Доступные: {list(self._sound_groups.keys())}")
            return False
        
        # Проверяем, не играет ли уже звук из этой группы (если нужно предотвращать наложение)
        should_prevent = self._should_prevent_overlap(group_name, prevent_overlap)
        if should_prevent and self.is_sound_playing(group_name):
            return False
        
        sound_group = self._sound_groups[group_name]
        
        # Временно меняем режим если указан
        original_mode = sound_group.mode
        if mode is not None:
            sound_group.mode = mode
        
        # Получаем звук для воспроизведения
        if specific_index is not None:
            sound = sound_group.get_specific_sound(specific_index)
        else:
            sound = sound_group.get_next_sound()
        
        # Восстанавливаем оригинальный режим
        if mode is not None:
            sound_group.mode = original_mode
        
        if sound is None:
            return False
        
        # Применяем вариации если нужно
        if apply_variations:
            sound = self._apply_variations(sound)
        
        # Устанавливаем громкость
        final_volume = self._audio_volume if volume is None else volume
        sound.set_volume(max(0.0, min(1.0, final_volume)))
        
        # Проигрываем звук
        channel = sound.play(loops=loops, fade_ms=fade_ms)
        
        if channel is not None:
            self._currently_playing[group_name] = channel
            return True
        
        return False
    
    def play_sound_loop(self, group_name: str, volume: Optional[float] = None, 
                       fade_ms: int = 0, prevent_overlap: Optional[bool] = None) -> bool:
        """Проигрывает звук в режиме зацикливания"""
        return self.play_sound(group_name, volume, loops=-1, fade_ms=fade_ms, 
                             mode=PlaybackMode.LOOP, prevent_overlap=prevent_overlap)
    
    def stop_sound(self, group_name: str) -> None:
        """Останавливает проигрывание звука из группы"""
        if group_name in self._currently_playing:
            channel = self._currently_playing[group_name]
            channel.stop()
            del self._currently_playing[group_name]
    
    def stop_all_sounds(self) -> None:
        """Останавливает все звуки этого объекта"""
        for channel in self._currently_playing.values():
            channel.stop()
        self._currently_playing.clear()
    
    def set_sound_group_mode(self, group_name: str, mode: PlaybackMode) -> None:
        """Устанавливает режим воспроизведения для группы звуков"""
        if group_name in self._sound_groups:
            self._sound_groups[group_name].mode = mode
    
    def set_audio_volume(self, volume: float) -> None:
        """Устанавливает громкость для всех звуков этого объекта"""
        self._audio_volume = max(0.0, min(1.0, volume))
    
    def get_available_sound_groups(self) -> List[str]:
        """Возвращает список доступных групп звуков"""
        if not hasattr(self, '_sound_groups'):
            self._init_audio_mixin()
        return list(self._sound_groups.keys())
    
    def is_sound_playing(self, group_name: str) -> bool:
        """Проверяет, играет ли звук из указанной группы"""
        if group_name not in self._currently_playing:
            return False
        
        channel = self._currently_playing[group_name]
        return channel.get_busy()
    
    def get_playing_sounds(self) -> List[str]:
        """Возвращает список групп, которые сейчас играют"""
        return [group_name for group_name, channel in self._currently_playing.items() 
                if channel.get_busy()]