import React from 'react';
import { observer } from 'mobx-react-lite';
import Editer from './views/editer/editer';

import './App.css';

function App() {
  return <Editer />;
}

export default observer(App);
