import { makeObservable, observable } from 'mobx';
import { ObjectAttribute } from '../models/drow-models';

interface GroundParams {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  color?: number[];
  __class__?: string;
}

class Ground {
  static __class__ = 'Ground';
  static __storageType__ = 'grounds';
  __class__ = 'Ground';
  __id__ = Math.random().toString(36).substr(2, 9);
  __storageType__ = 'grounds';
  x: number = 0;
  y: number = 0;
  width: number = 400;
  height: number = 50;
  color: number[] = [0, 155, 0];

  constructor(params: GroundParams = {}) {
    Object.assign(this, params);

    makeObservable(this, {
      x: observable,
      y: observable,
      width: observable,
      height: observable,
      color: observable,
    });
  }

  update(params: Partial<Ground>) {
    Object.assign(this, params);
  }

  toISOString() {
    return 'Ground';
  }

  toJSON() {
    return {
      __class__: Ground.__class__,

      x: this.x,
      y: this.y,
      width: this.width,
      height: this.height,
      color: [...this.color],
    };
  }

  description(): Record<string, ObjectAttribute> {
    return {
      x: { description: 'Координаты по оси X', type: 'NUMBER' },
      y: { description: 'Координаты по оси Y', type: 'NUMBER' },
      width: { description: 'Ширина землт', type: 'NUMBER' },
      height: { description: 'Высота земли', type: 'NUMBER' },
      color: { description: 'Цвет земли. Задается в формате RGB', type: 'COLOR' },
    };
  }
}

export { Ground };
