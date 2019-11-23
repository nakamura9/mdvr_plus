import React, {Component} from 'react';
import styles from './reminder.css';
import ReactDOM from 'react-dom';
import EventReminderForm from './reminder_form';


class EventReminderWidget extends Component {
    state = {
        events: [],
    }

    addReminder = (data)=>{
        let newState = [...this.state.events];
        newState.push(data);
        this.setState({
            events: newState,
        }, this.updateForm);
    }

    updateForm = () =>{
        const widget = document.getElementById('id_reminder_data');
        widget.value = encodeURIComponent(JSON.stringify(this.state.events))
    }

    deleteHandler = (index) =>{
        let newEvents = [...this.state.events];
        newEvents.splice(index, 1);
        this.setState({events: newEvents});
    }

    render(){
        return(
            <div>
                <table className='table'>
                    <thead>
                        <tr className='primary text-white'>
                            <th></th>
                            <th>Reminder Type</th>
                            <th>Value</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        {this.state.events.map((evt, i) =>(
                            <tr>
                                <td>{i + 1}</td>
                                <td>{evt.eventType}</td>
                                <td>{evt.value}</td>
                                <td>
                                    <button
                                      type='button'
                                      onClick={() => this.deleteHandler(i)}
                                      className="btn btn-sm btn-danger">
                                        <i className="fas fa-times"></i>
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                    <EventReminderForm 
                      insertHandler={this.addReminder}/>
                </table>
                
            </div>
        )
    }
}
const widgetRoot = document.getElementById('widget-root');

ReactDOM.render(<EventReminderWidget />, widgetRoot)