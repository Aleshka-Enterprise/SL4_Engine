import { Entity, Player } from "../classes/entities";
import { Ground } from "../classes/ground";

interface Figure {
  x: number;
  y: number;
  width: number;
  height: number;
  color: number[];
}

type SelectableEntity = Entity | Player | Ground;

interface ObjectAttribute {
  description: string;
  type: 'NUMBER' | 'STRING' | 'CHOOSE' | 'BOOLEAN' | 'COLOR' | 'BIND',
  min?: number;
  max?: number;
  options?: string[];
}

type Constructor<T> = new (...args: any[]) => T;

export type { Figure, ObjectAttribute, SelectableEntity, Constructor }