import React, { useEffect, useState } from 'react';
import { Entity, Player, Zombie } from '../../classes/entities';
import { observer } from 'mobx-react-lite';
import { storage } from '../../store/game-store';
import { Ground } from '../../classes/ground';
import { SelectableEntity } from '../../models/drow-models';
import './left-panel.scss';
import { Weapon } from '../../classes/weapon';

const LeftPanel = (): React.ReactElement => {
  const [options, setOptions] = useState<Record<string, unknown[]>>();
  const [expandedList, setExpandedList] = useState<Record<string, boolean>>({});

  useEffect(() => {
    const options = {
      'Entities (Сущности)': [Entity, Player, Zombie],
      'Ground (Земля)': [Ground],
      'Weapon (Оружие)': [Weapon],
    };

    const expandedList = {};

    Object.keys(options).forEach(el => {
      expandedList[el] = false;
    });

    setOptions(options);
    setExpandedList(expandedList);
  }, []);

  const onListToggle = (key: string) => {
    setExpandedList({ ...expandedList, [key]: !expandedList[key] });
  };

  const createObject = (e: React.MouseEvent<HTMLDivElement, MouseEvent>, template) => {
    e.stopPropagation();
    e.preventDefault();

    console.log(storage.windowCoordinates);

    const object = new template({ ...storage.windowCoordinates });
    const objectType = template.__storageType__;

    storage[objectType].push(object);
  };

  return (
    <div className="left-panel">
      {options &&
        Object.keys(options).map((el, index) => {
          return (
            <div className="category" key={index} onClick={(): void => onListToggle(el)}>
              {el}
              {expandedList[el] &&
                options[el].map((obj: SelectableEntity) => {
                  return (
                    <div
                      className="object"
                      key={obj.__class__}
                      onClick={(event): void => createObject(event, obj)}
                    >
                      {obj.__class__}
                    </div>
                  );
                })}
            </div>
          );
        })}
    </div>
  );
};

export default observer(LeftPanel);
