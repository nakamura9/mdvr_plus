import React from 'react';
import MiniCalendar from '../components/mini_calendar';
import styles from './sidebar.css';

const sidebar = (props) =>{
    const navHeight = document.getElementById('page-heading').offsetHeight;
    const height = document.documentElement.clientHeight - navHeight -2;
    return(
        <div id="sidebar" className={styles.sidebar} style={{height:height}}>
        <a href="/reports/create-reminder/"
        className="btn btn-secondary btn-block"> <i className="fas fa-plus"></i> Add Reminder</a>
            
            <div className="btn-group">
                <button
                    className="btn btn-secondary"
                    onClick={props.prevHandler}>
                        <i className="fas fa-arrow-left"></i>
                </button>    
                <button
                    className="btn btn-secondary"
                    onClick={props.nextHandler}>
                        <i className="fas fa-arrow-right"></i>
                </button>
            </div>
            <div>
                <MiniCalendar 
                    year={props.calendarState.year}
                    month={props.calendarState.month} />
            </div>
            
        </div>
    );
}

export default sidebar;