import React, {Component} from 'react';
import styles from './reminder.css';

class ReminderEventForm extends Component {
    state = {
        eventType: '0',
        date: null,
        mileage: null,
        daysB4: null
    }

    inputHandler = (field, evt) =>{
        console.log('called')
        let newState = {...this.state};
        newState[field] = evt.target.value;
        this.setState(newState);
    }

    addHandler =() =>{
        switch(this.state.eventType){
            case '0':
                if(!this.state.date){
                    alert('A date must be selected for the reminder');
                    return;
                }else{
                    this.props.insertHandler({
                        eventType: 'Date',
                        value: this.state.date
                    })
                }
                break;
            case '1':
                    if(!this.state.daysB4){
                        alert('The number of days ahead of the event need to be specified for this reminder');
                        return;
                    }else{
                        this.props.insertHandler({
                            eventType: 'Days Before Reminder',
                            value: this.state.daysB4
                        })
                    }
                    break;
            case '2':
                    if(!this.state.mileage){
                        alert('The mileage for this reminder must be specified befor proceeding');
                        return
                    }else{
                        this.props.insertHandler({
                            eventType: 'Mileage',
                            value: this.state.mileage
                        })

                    }
                    break;
        }
        this.resetFields();
    }

    resetFields(){
        console.log('reset!')
        this.setState({
            date: null,
            mileage: null,
            daysB4: null
        });
    }
    
    render(){

        let renderedWidget;
        switch(this.state.eventType){
            case '0':
                renderedWidget = <input type="date"
                                    className='form-control'
                                    placehoder='Date...'
                                    name='date' 
                                    value={this.state.date}
                                    onChange={evt => this.inputHandler('date', evt)}/>
                break;
            case '1':
                renderedWidget = <input type="number" 
                                    name='daysB4' 
                                    className='form-control'
                                    placeholder='# days before...'
                                    value={this.state.daysB4}
                                    onChange={evt => this.inputHandler('daysB4', evt)}/>
                break;
            case '2':
                renderedWidget = <input type="number" 
                                    value={this.state.mileage}
                                    name='mileage'
                                    className='form-control'
                                    placeholder='Mileage...'
                                    onChange={evt => this.inputHandler('mileage', evt)}/>
                break;
        }

        return(
            <tfoot>
                <tr>
                    <td></td>
                    <td>
                        <select name="event_type" 
                            id="id_event_type"
                            className='form-control'
                            value={this.state.eventType}
                            onChange={(evt) => {
                                this.setState({eventType: evt.target.value})
                                this.resetFields()
                            }}>
                            <option value={0} >Date</option>
                            <option value={1} >Days Before</option>
                            <option value={2} >Mileage</option>
                        </select>
                    </td>
                    <td colSpan={2}>{renderedWidget}</td>
                    
                </tr>
                <tr>
                    <td colSpan={4}>
                        <button 
                          type='button'
                          className="btn-primary btn btn-block"
                          onClick={this.addHandler}>
                            Add Reminder
                        </button>
                    </td>
                </tr>
            </tfoot>
        )
    }
}

export default ReminderEventForm;