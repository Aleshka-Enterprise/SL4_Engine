import { makeAutoObservable } from 'mobx';
import { Entity, Player } from '../classes/entities';
import { Constructor, SelectableEntity } from '../models/drow-models';
import { Ground } from '../classes/ground';

class GameStorage {
  entities: Entity[] = [];
  grounds: Ground[] = [];
  items = [];
  shots = [];
  selectedObject = null;
  camera = null;
  windowCoordinates: { x: number; y: number } = { x: 0, y: 0 };
  gameOptions = {
    running: true,
    clock_tick: 60,
  };
  clipboard: SelectableEntity | null = null;
  lastCopyPosition = { x: 0, y: 0 };

  constructor() {
    makeAutoObservable(this);
  }

  clear() {
    this.entities = [];
    this.grounds = [];
    this.items = [];
    this.shots = [];
    this.camera = null;
    this.windowCoordinates = { x: 0, y: 0 };
  }

  addEntity(entity: Entity) {
    this.entities.push(entity);
  }

  setSelectedObject(obj: SelectableEntity | null) {
    this.selectedObject = obj; // MobX автоматически отследит изменение
  }

  updateSelectedObject(partialObj: Partial<Entity>) {
    this.selectedObject?.update(partialObj);
  }

  copyToClipboard(obj: SelectableEntity) {
    if (!obj) return;

    // Создаем глубокую копию объекта
    const objCopy = JSON.parse(JSON.stringify(obj));

    // Проверяем, что конструктор существует и является функцией
    if (typeof obj.constructor !== 'function') {
      console.error('Object constructor is not a function');
      return;
    }

    try {
      // Создаем новый экземпляр через конструктор
      this.clipboard = new (obj.constructor as Constructor<SelectableEntity>)(objCopy);
      this.lastCopyPosition = { x: obj.x, y: obj.y };
    } catch (error) {
      console.error('Failed to copy object:', error);
    }
  }

  createFromJSON(json: { __class__: string }) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const classes: Record<string, any> = {
      Entity,
      Player,
      Ground, // добавить другие классы по необходимости
    };

    const cls = classes[json.__class__];
    if (!cls) return null;

    return new cls(json);
  }

  pasteFromClipboard(offset = 20) {
    if (!this.clipboard) return null;

    const json = JSON.parse(JSON.stringify(this.clipboard));
    const newObj = this.createFromJSON(json);

    if (!newObj) return null;

    // Смещаем относительно исходной позиции
    newObj.x = this.lastCopyPosition.x + offset;
    newObj.y = this.lastCopyPosition.y + offset;
    this.lastCopyPosition = { x: newObj.x, y: newObj.y };

    // Добавляем в хранилище
    if (newObj.__storageType__ === 'entities') {
      this.addEntity(newObj);
    } else if (newObj.__storageType__ === 'grounds') {
      this.grounds.push(newObj);
    }

    return newObj;
  }
}

export const storage = new GameStorage();
