import { makeObservable, observable, action } from 'mobx';
import { ObjectAttribute } from '../models/drow-models';

interface WeaponParams {
  __storageType__?: string;
  offset_x?: number;
  offset_y?: number;
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  color?: number[];
  entity?: null;
  cooling_down?: number;
  maximum_number_of_bullets?: number;
  delete_after_death?: boolean;
  gravity?: number;
  no_ready_color?: number[];
}

// Базовый класс Weapon
class Weapon {
  static __class__ = 'Weapon';
  static __storageType__ = 'items';
  __class__ = 'Weapon';
  __storageType__ = 'items';
  x = 0;
  y = 0;
  offset_x = 0;
  offset_y = 0;
  width = 15;
  height = 5;
  color: number[] = [1, 1, 1];
  entity = null;
  cooling_down = 30;
  maximum_number_of_bullets = 10;
  delete_after_death = false;
  gravity = 0.7;
  no_ready_color = [1, 1, 1];
  __id__ = Math.random().toString(36).substr(2, 9);

  constructor(params: WeaponParams = {}) {
    Object.assign(this, params);

    makeObservable(this, {
      x: observable,
      y: observable,
      offset_x: observable,
      offset_y: observable,
      width: observable,
      height: observable,
      color: observable,
      entity: observable,
      cooling_down: observable,
      maximum_number_of_bullets: observable,
      delete_after_death: observable,
      gravity: observable,
      no_ready_color: observable,
    });
  }

  toISOString() {
    return 'Weapon';
  }

  toJSON() {
    return {
      __class__: Weapon.__class__,

      x: this.x,
      y: this.y,
      offset_x: this.offset_x,
      offset_y: this.offset_y,
      width: this.width,
      height: this.height,
      color: [...this.color],
      entity: this.entity,
      cooling_down: this.cooling_down,
      maximum_number_of_bullets: this.maximum_number_of_bullets,
      delete_after_death: this.delete_after_death,
      gravity: this.gravity,
      no_ready_color: [...this.no_ready_color],
    };
  }

  update(params: Partial<Weapon>) {
    Object.assign(this, params);
  }

  description(): Record<string, ObjectAttribute> {
    return {
      x: { description: 'Координаты по оси X', type: 'NUMBER' },
      y: { description: 'Координаты по оси Y', type: 'NUMBER' },
      offset_x: { description: 'Отступ по оси x относительно владельца оружя', type: 'NUMBER' },
      offset_y: { description: 'Отступ по оси x относительно владельца оружя', type: 'NUMBER' },
      width: { description: 'Ширина объекта', type: 'NUMBER' },
      height: { description: 'Высота объекта', type: 'NUMBER' },
      color: { description: 'Цвет объекта. Задается в формате RGB', type: 'COLOR' },
      cooling_down: { description: 'Время остывания оружия', type: 'NUMBER' },
      maximum_number_of_bullets: {
        description: 'Максимальное кол-во пуль на экране',
        type: 'NUMBER',
      },
      delete_after_death: {
        description: 'Нужно ли удалять оружие после смерти владельца',
        type: 'BOOLEAN',
      },
      gravity: { description: 'Гравитация. Сила с какой будет падать объект', type: 'NUMBER' },
    };
  }
}

export { Weapon };
