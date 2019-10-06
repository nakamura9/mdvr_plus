import React, {Component} from 'react';
import axios from 'axios'
import Radium from 'radium';
import styles from './mini_calendar.css';

//being called repeatedly affecting performance
const rangeFunc = (start, end) =>{
    let vals = [];
    let i;

    for(i=start; i<end; i++){
        vals.push(i);
    }
    return vals

}

const MonthChooser  = (props) =>{
    return(
        <div>
            <select name="" id="" onChange={props.handleMonth}>
                <option value="">Select Month</option>
                {['January', 'Febuary', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'].map((m,i) =>(<option key={i} value={i+1}>{m}</option>))}
            </select>
            <select name="" id="" onChange={props.handleYear}>
                <option value="">Select Year</option>
                {rangeFunc(2000, 2050).map((i) =>(
                    <option key={i} value={i}>{i}</option>
                ))}
            </select>
            <button className="btn" onClick={props.goToMonth}>Go</button>
        </div>
        )
}

class  MiniCalendar extends Component{
    state = {
        weeks: [],
        editing: false,
        month: null,
        year: null,
    }

    
    componentDidUpdate(prevProps, prevState){
        if(this.props.year !== prevProps.year || this.props.month !== this.props.month){
            axios({
                method: 'GET',
                url: `/reports/api/month/${this.props.year}/${this.props.month}`
            }).then(res =>{
                this.setState({
                    weeks: res.data.weeks,
                    period: res.data.period_string
                })
            })
        }
    }

    handleMonth =(evt) =>{
        if( evt.target.value != ""){
            this.setState({month: evt.target.value});
        }
    }
    handleYear =(evt) =>{
        if( evt.target.value != ""){
            this.setState({year: evt.target.value});
        }
    }

    goToMonth = () =>{
        if(this.state.month && this.state.year){
            const splitURL = window.location.href.split('/')
            const len = splitURL.length
            let newURL = [...splitURL]
            newURL[len-3] = this.state.year //set year
            newURL[len-2] = this.state.month //set month
            window.location.replace(newURL.join('/'))
        }
    }
    
    render(){
        return(
            <div>
            {this.state.editing ? 
                <MonthChooser 
                    handleMonth={this.handleMonth}
                    handleYear={this.handleYear}
                    goToMonth={this.goToMonth} />
            :
                <h4 
                    className={styles.title}
                    onClick={() => {this.setState({editing: true})}}>{this.state.period}</h4>
                
        }
            <table className={styles.miniTable}>
                <tbody>
                    <tr>
                        <th>Mo</th>
                        <th>Tu</th>
                        <th>We</th>
                        <th>Th</th>
                        <th>Fr</th>
                        <th>Sa</th>
                        <th>Su</th>
                    </tr>
                    {this.state.weeks.length === 0
                        ? <tr>
                            <td colSpan={7}>Loading data...</td>
                        </tr>
                        : null
                    }
                    {this.state.weeks.map((week, i) =>(
                        <tr key={i}>

                            {week.map((day, j) =>(
                                <td key={j} style={{padding:'3px'}}>
                                    <a key={i.toString() + '-' + j.toString()}
                                        style={{
                                            textDecoration: "none",
                                        color: (i==0 && day.day > 7) || (i == 4 && day.day < 7)
                                        ? '#bbb' 
                                        : 'white' ,
                                        width:" 100%",
                                        display: 'inline-block',
                                        ":hover": {
                                            color: '#999',
                                            backgroundColor: 'white'
                                        }
                                    }}>{day.day}</a></td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
            </div>
        );
    }
}



export default Radium(MiniCalendar);