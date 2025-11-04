import { makeObservable, observable, action } from 'mobx';
import { ObjectAttribute } from '../models/drow-models';
import { storage } from '../store/game-store';

interface EntityParams {
  __storageType__?: string;
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  color?: number[];
  speed?: number;
  hp?: number;
  gravity?: number;
  jump_force?: number;
  direction?: 'left' | 'right';
  boost?: number;
  show_hp?: boolean;
  weapon?: null;
}

// Базовый класс Entity
class Entity {
  static __class__ = 'Entity';
  static __storageType__ = 'entities';
  __class__ = 'Entity';
  __storageType__ = 'entities';
  x = 0;
  y = 0;
  width = 100;
  height = 100;
  color: number[] = [1, 1, 1];
  speed = 0;
  hp = 1;
  gravity = 1;
  jump_force = -24;
  direction: 'left' | 'right' = 'left';
  boost = 5;
  show_hp = false;
  weapon = null;
  __id__ = Math.random().toString(36).substr(2, 9);

  constructor(params: EntityParams = {}) {
    Object.assign(this, params);

    makeObservable(this, {
      x: observable,
      y: observable,
      width: observable,
      height: observable,
      color: observable,
      speed: observable,
      hp: observable,
      gravity: observable,
      jump_force: observable,
      direction: observable,
      boost: observable,
      show_hp: observable,
      weapon: observable,
      update: action,
    });
  }

  toISOString() {
    return 'Entity';
  }

  toJSON() {
    return {
      __class__: Entity.__class__,
      x: this.x,
      y: this.y,
      width: this.width,
      height: this.height,
      color: [...this.color],
      speed: this.speed,
      hp: this.hp,
      gravity: this.gravity,
      jump_force: this.jump_force,
      direction: this.direction,
      boost: this.boost,
      show_hp: this.show_hp,
      weapon: this.weapon,
    };
  }

  update(params: Partial<Entity>) {
    Object.assign(this, params);
  }

  description(): Record<string, ObjectAttribute> {
    return {
      x: { description: 'Координаты по оси X', type: 'NUMBER' },
      y: { description: 'Координаты по оси Y', type: 'NUMBER' },
      width: { description: 'Ширина объекта', type: 'NUMBER' },
      height: { description: 'Высота объекта', type: 'NUMBER' },
      color: { description: 'Цвет объекта. Задается в формате RGB', type: 'COLOR' },
      speed: { description: 'Скорость объекта', type: 'NUMBER' },
      hp: { description: 'Количество жизни', type: 'NUMBER' },
      gravity: { description: 'Гравитация. Сила с какой будет падать объект', type: 'NUMBER' },
      jump_force: {
        description: 'Сила прыжка (отрицательная, т.к. ось Y направлена вниз)',
        type: 'NUMBER',
        min: 0,
      },
      direction: { description: 'Направление объекта', type: 'CHOOSE', options: ['left', 'right'] },
      boost: { description: 'Ускорение при беге', type: 'NUMBER' },
      show_hp: { description: 'Показывать ли здоровье', type: 'BOOLEAN' },
      weapon: { description: 'Оружие', type: 'BIND', options: storage.items },
    };
  }
}

// Класс Player
class Player extends Entity {
  static __class__ = 'Player';
  static __storageType__ = 'entities';
  __class__ = 'Player';
  energy = 350;
  color: number[] = [250, 0, 0];
  height: number = 100;
  width: number = 50;

  constructor(params: EntityParams & { energy?: number } = {}) {
    super(params);
    this.energy = params.energy ?? 350;
    this.__class__ = 'Player';

    makeObservable(this, {
      energy: observable,
    });
  }

  toISOString() {
    return 'Player';
  }

  toJSON() {
    const res = super.toJSON();
    return { ...res, energy: this.energy, __class__: Player.__class__ };
  }

  description() {
    return {
      ...super.description(),
      energy: { description: 'Энергия игрока', type: 'NUMBER' },
    } as Record<string, ObjectAttribute>;
  }
}

// Класс Player
class Zombie extends Entity {
  static __class__ = 'Zombie';
  static __storageType__ = 'entities';
  __class__ = 'Zombie';
  color: number[] = [250, 0, 0];
  height: number = 100;
  width: number = 50;

  constructor(params: EntityParams & { energy?: number } = {}) {
    super(params);
    this.__class__ = 'Zombie';
  }

  toISOString() {
    return 'Zombie';
  }

  toJSON() {
    const res = super.toJSON();
    return { ...res, __class__: Player.__class__ };
  }

  description() {
    return {
      ...super.description(),
    } as Record<string, ObjectAttribute>;
  }
}

export { Entity, Player, Zombie };
