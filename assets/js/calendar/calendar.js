import React from 'react';
import ReactDOM from 'react-dom';
import CalendarRouter from './container/Root';

console.log('calendar')
const calendar = document.getElementById('calendar-root');
console.log(calendar)
if(calendar){
    ReactDOM.render(<CalendarRouter />, calendar);
}