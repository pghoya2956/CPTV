import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import reportWebVitals from './reportWebVitals';
import KakaoMap from "./pages/KakaoMap";
import Map from "./Components/Map";
import List from "./Components/List"




ReactDOM.render(

  <>
    <Map />
  </>,
  document.getElementById('mapcontain')
);



ReactDOM.render(
<>
  <List />
</>,
document.getElementById('listcontain')
);

reportWebVitals();
