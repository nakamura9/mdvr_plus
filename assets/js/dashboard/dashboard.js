import 'babel-polyfill';
import React, {Component} from 'react';
import styles from './dashboard.css';
import ReactDOM from 'react-dom';
import axios from 'axios';

class Dashboard extends Component{
    state = {
        online: null,
        offline: null,
        moving: null,
        idling: null,
        session: null,
        host: null,
        port: null,
        vehicle_ids: [],
        tempVehicleList: [],
        vehicles: []

    }

    decToBin(num){
        //used to read status bytes 
        const numShifted = `${num}`*1;
        return numShifted.toString(2)
    }

    componentDidMount(){
        //get login data from the server
        axios({
            url: '/app/api/config/1',
            method: "GET"
        }).then(res =>{
        //login to the api
            const url = `http://${res.data.host}:${res.data.server_port}/StandardApiAction_login.action?account=${res.data.conn_account}&password=${res.data.conn_password}`;
            
            this.setState({
                host: res.data.host,
                port: res.data.server_port
            })
            
            axios({
                url: url,
                method: 'GET'
            }).then(res =>{
                //get the session
                this.setState({session: res.data.jsession}, 
                    () => {
                        // get the vehicle list
                        axios({
                            url: `http://${this.state.host}:${this.state.port}/StandardApiAction_getDeviceOlStatus.action?jsession=${this.state.session}`,
                            method: 'GET'
                        }).then(res =>{
                            this.setState({
                                vehicle_ids: res.data.onlines.map(
                                    data => data.did)
                                }, this.updateDashboard)
                        })
                    });
            })
        })
    }

    updateDashboard = () =>{
        this.state.vehicle_ids.forEach(id=>{
            let url = `http://${this.state.host}:${this.state.port}/StandardApiAction_getDeviceStatus.action?jsession=${this.state.session}&devIdno=${id}`
            axios({
                url: url,
                method: 'GET',
            }).then(res =>{
                let status = res.data.status[0];
                let newVehicleData = [...this.state.tempVehicleList]
                
                newVehicleData.push({
                    id: status.id,
                    //all states must be matched with an online Vehicle
                    moving: status.sp > 0 && status.ol == 1,
                    //to check idling the speed must be zero and the ACC must be on
                    idling: status.sp == 0 && this.decToBin(status.s1)[1] ==1
                        && status.ol == 1,
                    timestamp: status.gt,
                    plate: status.vid,
                    status: status.ol == 1 ? 'Online' : "Offline"
                })
                this.setState({tempVehicleList: newVehicleData})
            })
        })

        const newVehicleData = this.state.tempVehicleList;
        console.log(newVehicleData.filter(vehicle=>vehicle.status=="Offline").length)
        this.setState({
            vehicles: newVehicleData,
            online: newVehicleData.filter(
                vehicle=>vehicle.status == "Online").length,
            offline: newVehicleData.filter(
                vehicle=>vehicle.status == "Offline").length,
            moving: newVehicleData.filter(vehicle=>vehicle.moving).length,
            idling: newVehicleData.filter(vehicle=>vehicle.idling).length,
            tempVehicleList: []
        })
        
        //call after 5 seconds
        setTimeout(this.updateDashboard, 5000)
    }

    render(){
        return(
            <div className="container-fluid">
                <div className="row">
                    <div className="col-sm-12 col-md-3">
                        <div className={"card " +styles.dash_card} 
                        style={{borderTopColor: 'green'}}>
                            <div className="card-body">
                                <h3>Online Vehicles</h3>
                                {this.state.online != null
                                    ? <h1>{this.state.online}</h1>
                                    : <img className={styles.imgCenter} width='55' height='55' src='/static/common/images/spinner.gif'/>
                                }
                            </div>
                        </div>
                    </div>
                    <div className="col-sm-12 col-md-3">
                        <div className={"card " +styles.dash_card}
                            style={{borderTopColor: 'red'}}>
                            <div className="card-body">
                                <h3>Moving Vehicles</h3>
                                {this.state.moving != null 
                                    ? <h1>{this.state.moving}</h1>
                                    : <img className={styles.imgCenter} width='55' height='55' src='/static/common/images/spinner.gif'/>
                                }
                            </div>
                        </div>
                    </div>
                    <div className="col-sm-12 col-md-3">
                        <div className={"card " +styles.dash_card}>
                            <div className="card-body">
                                <h3>Idling Vehicles</h3>
                                {this.state.idling != null 
                                    ? <h1>{this.state.idling}</h1>
                                    : <img className={styles.imgCenter} width='55' height='55' src='/static/common/images/spinner.gif'/>
                                }
                            </div>
                        </div>
                    </div>
                    <div className="col-sm-12 col-md-3">
                        <div className={"card " +styles.dash_card}
                            style={{borderTopColor: 'grey'}}>
                            <div className="card-body">
                                <h3>Offline Vehicles</h3>
                                {this.state.offline != null
                                    ? <h1>{this.state.offline}</h1>
                                    : <img className={styles.imgCenter} width='55' height='55' src='/static/common/images/spinner.gif'/>
                                }
                            </div>
                        </div>
                    </div>
                </div>
                <hr className="my-4"/>
                <div className="row">
                    <div className="col-12">
                    <table className="table">
                        <thead>
                            <tr className='primary text-white'>
                                <th></th>
                                <th>Vehicle</th>
                                <th>Registration</th>
                                <th>Status</th>
                                <th>Last Update</th>
                            </tr>
                        </thead>
                        <tbody>
                            { this.state.vehicles.length > 0
                                ? this.state.vehicles.map((vehicle) =>{
                                    return(
                                        <tr key={vehicle.id}>
                                            {/*
                                            The color of the icon depends on the status of the vehicle. Offline vehicles are grey, moving vehicles are red, idling vehicles are blue and stationary online vehicles are green.
                                            */}
                                            <td><i className={"fas fa-truck " + styles.icon} style={{
                                                color: vehicle.status == "Online" ? 
                                                    vehicle.moving ? "red" : vehicle.idling ? "blue" : "green"
                                                : "grey"
                                                
                                            }}></i></td>
                                            <td>{vehicle.id}</td>
                                            <td>{vehicle.plate}</td>
                                            <td>{vehicle.status}</td>
                                            <td>{vehicle.timestamp}</td>
                                        </tr>
                                    )
                                })
                                : <tr>
                                    <td colSpan={5}>
                                        <img className={styles.imgCenter} width='55' height='55' src='/static/common/images/spinner.gif'/>
                                    </td>
                                </tr>
                                 }
                        </tbody>
                    </table>
                    </div>
                </div>
            </div>
        )
    }
}


const root = document.getElementById('root');
ReactDOM.render(<Dashboard />, root);