import React, { useEffect } from 'react';
import LeftPanel from '../../components/left-panel/left-panel';
import SVGEditor from '../../components/svg-editer/SVGEditor';
import { Player } from '../../classes/entities';
import { storage } from '../../store/game-store';
import { observer } from 'mobx-react-lite';
import RightPanel from '../../components/right-panel/right-panel';
import { saveLevel } from '../../utils/fileUtils';

import './editer.scss';

const Editer = (): React.ReactElement => {
  useEffect(() => {
    storage.addEntity(new Player());
  }, []);

  return (
    <>
      <button className="save" onClick={() => saveLevel()}>
        Сохранить JSON
      </button>
      <div className="editer">
        <LeftPanel />
        <SVGEditor />
        <RightPanel />
      </div>
    </>
  );
};

export default observer(Editer);
