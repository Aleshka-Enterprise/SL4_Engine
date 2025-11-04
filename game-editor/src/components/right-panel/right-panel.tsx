import React from 'react';
import { observer } from 'mobx-react-lite';
import { storage } from '../../store/game-store';

import './right-panel.scss';

const RightPanel = observer(() => {
  const { selectedObject } = storage;

  // Получаем описания напрямую из selectedObject
  const attributDescriptions = selectedObject?.description() || {};

  const rgbToHex = (color: number[]): string => {
    const componentToHex = (c: number) => {
      const hex = c.toString(16);
      return hex.length == 1 ? '0' + hex : hex;
    };

    return '#' + color.map(c => componentToHex(c)).join('');
  };

  const hexToRgb = (color: string) => {
    const r = parseInt(color.substr(1, 2), 16);
    const g = parseInt(color.substr(3, 2), 16);
    const b = parseInt(color.substr(5, 2), 16);
    return [r, g, b];
  };

  const inputField = (attrName: string): React.ReactElement => {
    const attributDescription = attributDescriptions[attrName];
    let input = <></>;

    if (!attributDescription) {
      return input;
    }

    if (attributDescription.type === 'NUMBER') {
      input = (
        <input
          title={attributDescription?.description}
          onChange={e => {
            storage.updateSelectedObject({ [attrName]: parseInt(e.target.value) || '' });
          }}
          value={selectedObject[attrName]}
        ></input>
      );
    } else if (attributDescription.type === 'BOOLEAN') {
      input = (
        <input
          title={attributDescription?.description}
          onChange={e => {
            selectedObject[attrName] = !selectedObject[attrName];
            storage.updateSelectedObject({ [attrName]: e.target.value });
          }}
          checked={selectedObject[attrName]}
          type="checkbox"
        ></input>
      );
    } else if (attributDescription.type === 'COLOR') {
      input = (
        <input
          type="color"
          value={rgbToHex(selectedObject[attrName])}
          onChange={e => storage.updateSelectedObject({ [attrName]: hexToRgb(e.target.value) })}
        />
      );
    } else if (attributDescription.type === 'CHOOSE') {
      input = (
        <select
          value={selectedObject[attrName]}
          onChange={e => storage.updateSelectedObject({ [attrName]: e.target.value })}
        >
          {attributDescription.options?.map((option: string | number) => {
            return (
              <option key={option} value={option}>
                {option}
              </option>
            );
          })}
        </select>
      );
    } else if (attributDescription.type === 'BIND') {
      input = (
        <select
          value={selectedObject[attrName]}
          onChange={e => storage.updateSelectedObject({ [attrName]: e.target.value })}
        >
          {[{ __id__: null }, ...attributDescription.options]?.map((option: { __id__: string }) => {
            return (
              <option key={option.__id__} value={option.__id__}>
                {option.__id__}
              </option>
            );
          })}
        </select>
      );
    }

    return (
      <div key={attrName}>
        <label>{attrName}</label>
        <div>{input}</div>
      </div>
    );
  };

  return (
    <div className="right-panel">
      {selectedObject && (
        <>
          {Object.keys(attributDescriptions).map(attr => inputField(attr))}
          <button
            className="delete"
            onClick={(): void => {
              const key = selectedObject.__storageType__;
              storage[key] = storage[key].filter(el => el != selectedObject);
              storage.selectedObject = null;
            }}
          >
            Удалить
          </button>
        </>
      )}
    </div>
  );
});

export default RightPanel;
