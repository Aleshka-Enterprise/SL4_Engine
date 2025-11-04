/* eslint-disable @typescript-eslint/no-explicit-any */
import { storage } from '../store/game-store';
import { Entity, Player } from '../classes/entities';
import { Weapon } from '../classes/weapon';

const CLASS_REGISTRY = { Entity, Player, Weapon };

// Сериализация объекта
function serializeObj(obj: any, _seen: Set<string> = new Set()): object {
  // Обработка примитивов и null/undefined
  if (obj === null || typeof obj !== 'object') return obj;

  // Обработка массивов
  if (Array.isArray(obj)) {
    return obj.map(item => serializeObj(item, _seen));
  }

  // Обработка дат
  if (obj instanceof Date) {
    return { __class__: 'Date', __value__: obj.toISOString() };
  }

  const objId = obj.__id__ || Math.random().toString(36).substr(2, 9);
  if (_seen.has(objId)) return { __ref__: objId };
  _seen.add(objId);

  // Для обычных объектов и классов
  const result: any = {
    __class__: obj.__class__ || 'Object',
    __id__: objId,
  };

  // Специальная обработка для Rect (если используется)
  if (obj.__class__ === 'Rect') {
    return {
      __class__: 'Rect',
      x: obj.x,
      y: obj.y,
      width: obj.width,
      height: obj.height,
    };
  }

  // Для обычных объектов
  const attributes: any = {};
  for (const [key, value] of Object.entries(obj)) {
    if (key.startsWith('__')) continue;

    // Пропускаем функции
    if (typeof value === 'function') continue;

    attributes[key] = serializeObj(value, _seen);
  }

  result.attributes = attributes;
  return result;
}

// Десериализация объекта
function deserializeObj(data: any, createdObjects: Record<string, any> = {}): any {
  if (data === null || typeof data !== 'object') return data;

  // Восстановление массива
  if (Array.isArray(data)) {
    return data.map(item => deserializeObj(item, createdObjects));
  }

  // Обработка ссылок
  if (data.__ref__) return createdObjects[data.__ref__];

  // Восстановление даты
  if (data.__class__ === 'Date') {
    return new Date(data.__value__);
  }

  // Восстановление Rect
  if (data.__class__ === 'Rect') {
    return {
      __class__: 'Rect',
      x: data.x,
      y: data.y,
      width: data.width,
      height: data.height,
    };
  }

  // Для обычных объектов
  const ClassConstructor = CLASS_REGISTRY[data.__class__] || Object;
  const obj = new ClassConstructor();

  if (data.__id__) createdObjects[data.__id__] = obj;

  if (data.attributes) {
    for (const [key, value] of Object.entries(data.attributes)) {
      obj[key] = deserializeObj(value, createdObjects);
    }
  }

  return obj;
}

// Сохранение уровня в файл
export async function saveLevel(filename: string = 'level.json'): Promise<boolean> {
  const levelData = {
    entities: storage.entities.map(obj => serializeObj(obj)),
    grounds: storage.grounds.map(obj => serializeObj(obj)),
    items: storage.items.map(obj => serializeObj(obj)),
    camera: serializeObj(storage.camera),
    gameOptions: storage.gameOptions,
  };

  try {
    // Используем традиционный метод сохранения через <a> для максимальной совместимости
    const blob = new Blob([JSON.stringify(levelData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    return true;
  } catch (error) {
    console.error('Ошибка сохранения:', error);
    return false;
  }
}

// Загрузка уровня из файла
export async function loadLevel(): Promise<boolean> {
  return new Promise(resolve => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';

    input.onchange = async e => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) {
        resolve(false);
        return;
      }

      try {
        const content = await file.text();
        const levelData = JSON.parse(content);

        storage.clear();
        const createdObjects: Record<string, any> = {};

        storage.entities = (levelData.entities || [])
          .map((e: any) => deserializeObj(e, createdObjects))
          .filter(Boolean);

        storage.grounds = (levelData.grounds || [])
          .map((g: any) => deserializeObj(g, createdObjects))
          .filter(Boolean);

        if (levelData.camera) {
          storage.camera = deserializeObj(levelData.camera, createdObjects);
        }

        storage.gameOptions = levelData.gameOptions || {};

        resolve(true);
      } catch (error) {
        console.error('Ошибка загрузки:', error);
        resolve(false);
      }
    };

    input.click();
  });
}
