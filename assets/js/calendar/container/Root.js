import React, {Component} from 'react';
import Month from '../components/Month/Month';
import {BrowserRouter as Router, Route, Link} from 'react-router-dom';
import Sidebar from '../components/sidebar';

export default class CalendarRouter extends Component{
    state = {
        year: 2018,
        month: 1,
        day: 1,
        nextLink: "",
        prevLink: "",
        windowWidth: 135,
        windowHeight: 95
    }

    nextHandler = () =>{
        this.setLinks();
        window.location.replace(this.state.nextLink);
    }
    prevHandler = () =>{
        this.setLinks();
        window.location.replace(this.state.prevLink);
    }

    componentDidMount(){
        this.setLinks();
        // calculate the cell width
        // get the screen width
        // subtract the sidebar width
        // divide by 7
        // subtract the padding and border widths 
        this.setState({windowWidth: Math.floor(
            ((window.screen.width -250) / 7) - 12)});
        this.setState({windowHeight: 58});

    }

    setLinks = () =>{
        // for setting mini calendar
        const splitURL = window.location.href.split("/");
        const type = splitURL[4];
        console.log(splitURL)
        // numbered normally
        let dateData = {
            month: splitURL[6],
            year: splitURL[5],
            day: 1
        }
        this.setState(dateData);

        if(type === "month"){
            // month ranges from 0 - 11 
            // url ranges from 1 -12 
            // therefore next month is the same
            let nextDate = new Date(dateData.year, dateData.month, 1);
            //subtract one for the date mode and another one for the deduction
            let prevDate = new Date(dateData.year, dateData.month - 2, 1);

            // add 1 to each month to represent the normal representation of the month
            this.setState({
                prevLink: `/calendar/month/${prevDate.getFullYear()}/${prevDate.getMonth() + 1}`,
                nextLink: `/calendar/month/${nextDate.getFullYear()}/${nextDate.getMonth() + 1}`
            });
            
        }
    }
    

    render(){
        return(
            <Router>
                <div >
                    <Sidebar calendarState={{...this.state}}
                            nextHandler={this.nextHandler}
                            prevHandler={this.prevHandler}/>
                    <div style={{
                        display:'inline-block', 
                        float: 'left', 
                    'width':'500px',
                        clear: 'right'}}>

                        <Route 
                            path="/calendar/month/:year/:month" 
                            render={(props) => 
                                <Month width={this.state.windowWidth} 
                                        height={this.state.windowHeight}
                                        {...props} 
                                        linkUpdater={this.setLinks}/>} />
                        
                    </div>
                </div>
            </Router>
        )
    }
    
}