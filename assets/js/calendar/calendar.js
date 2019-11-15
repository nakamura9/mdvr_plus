import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import CalendarRouter from './container/Root';


const calendar = document.getElementById('calendar-root');

if(calendar){
    ReactDOM.render(<CalendarRouter />, calendar);
}