import 'babel-polyfill';
import React, {Component} from 'react';
import styles from './dashboard.css';
import ReactDOM from 'react-dom';
import axios from 'axios';
import { Map, Marker, Popup, TileLayer } from 'react-leaflet'



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
        vehicles: [],
        mapLat: -18.6652,
        mapLng: 30.3560

    }

    decToBin(num){
        //used to read status bytes 
        //needs to convert bytes to 32 bits
        const numShifted = `${num}`*1;
        const bits = numShifted.toString(2);
        const padding = new Array(32 - bits.length)
                                .fill(0)
                                .join('');
        return padding + bits


    }


    linkClickHandler = (lat, lng) =>{
        this.setState({
            mapLat: lat,
            mapLng: lng
        })
    }

  


    getVehicleList = () =>{
        axios({
            url: `http://${this.state.host}:${this.state.port}/StandardApiAction_getDeviceOlStatus.action?jsession=${this.state.session}`,
            method: 'GET'
        }).then(res =>{
            this.setState({
                vehicle_ids: res.data.onlines.map(
                    data => data.did)
                }, this.updateDashboard)
        })
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
            }, () =>{
                axios({
                    url: url,
                    method: 'GET'
                }).then(res =>{
                    //get the session
                    this.setState({session: res.data.jsession}, 
                        this.getVehicleList);
            })
        })
        })
    }

    updateDashboard = () =>{
        const updatePromises = this.state.vehicle_ids.map(id=>{
            let url = `http://${this.state.host}:${this.state.port}/StandardApiAction_getDeviceStatus.action?jsession=${this.state.session}&devIdno=${id}&toMap=1`
            return axios({
                url: url,
                method: 'GET',
            }).then(res =>{
                let status = res.data.status[0];
                const statusBits = this.decToBin(status.s1)
                const accStatus = statusBits[30] //for bit 1
                return({
                    id: status.id,
                    //all states must be matched with an online Vehicle
                    moving: status.sp > 0 && status.ol == 1,
                    //to check idling the speed must be zero and the ACC must be on
                    idling: status.sp == 0 && accStatus ==1
                        && status.ol == 1,
                    timestamp: status.gt,
                    location: `${status.mlat}, ${status.mlng}`,
                    lat: status.mlat,
                    lng: status.mlng,
                    status: status.ol == 1 ? 'Online' : "Offline"
                })
            })
        })
        Promise.all(updatePromises).then((newVehicleData) =>{
            this.setState({
                vehicles: newVehicleData,
                online: newVehicleData.filter(
                    vehicle=>vehicle.status == "Online").length,
                offline: newVehicleData.filter(
                    vehicle=>vehicle.status == "Offline").length,
                moving: newVehicleData.filter(vehicle=>vehicle.moving).length,
                idling: newVehicleData.filter(vehicle=>vehicle.idling).length,
            })
        
            //call after 5 seconds
            setTimeout(this.updateDashboard, 5000)
            
        })

        
    }

    render(){
        return(
            <div className="container-fluid">
                <div className="row">
                    <div className="col-sm-12 col-md-3">
                        <div className={"card " +styles.dash_card} 
                        style={{borderTopColor: 'red'}}>
                            <div className="card-body">
                            <i className="fas fa-wifi fa-7x   " style={{position:'absolute', opacity:0.4, transform: 'rotateZ(30deg)'}}></i>
                                
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
                            style={{borderTopColor: 'green'}}>
                            <div className="card-body">
                            <i className="fas fa-truck fa-7x   " style={{position:'absolute', opacity:0.4}}></i>

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
                            <i className="fas fa-traffic-light fa-7x   " style={{position:'absolute', opacity:0.4}}></i>

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
                            <i className="fas fa-power-off fa-7x   " style={{position:'absolute', opacity:0.4, transform: 'rotateZ(30deg)'}}></i>
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
                    <div className="col-md-3 col-sm-12" style={{maxHeight: '100vh', overlfowY: 'auto'}}>
                            { this.state.vehicles.length > 0
                                ? this.state.vehicles.map((vehicle) =>{
                                    return(
                                        <div key={vehicle.id} className="card">
                                            <div className="row">
                                                <div className="col-4" style={{display:'flex', justifyContent: 'center',alignItems:'center'}}>
                                                <i className={"fas fa-truck " + styles.icon} style={{
                                                    fontSize: '3rem',
                                                    color: vehicle.status == "Online" ? 
                                                        vehicle.moving ? "green" : vehicle.idling ? "blue" : "red"
                                                    : "grey"
                                                    
                                                }}></i>
                                                </div>
                                                <div className="col-8">
                                                    <h6>{vehicle.id}</h6>
                                                    <p>{vehicle.status}</p>
                                                    <p><button className='btn btn-sm'
                                                        onClick={() => this.linkClickHandler(vehicle.lat, vehicle.lng)}
                                                        href={`/reports/map/${vehicle.lat}/${vehicle.lng}`}><i  className="fas fa-map"></i>{vehicle.location}</button></p>
                                                    <p><i class="fas fa-stopwatch    "></i> {vehicle.timestamp}</p>
                                                </div>
                                            </div>
                                        </div>
                                        
                                    )
                                })
                                : 
                                    <img className={styles.imgCenter} width='55' height='55' src='/static/common/images/spinner.gif'/>    
                                 }
                    </div>
                    <div className="col-md-9 col-sm-12" >
                    <Map center={[this.state.mapLat, this.state.mapLng]} zoom={10}>
                        <TileLayer
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        attribution="&copy; <a href=&quot;http://osm.org/copyright&quot;>OpenStreetMap</a> contributors"
                        />
                        {this.state.vehicles.map((vehicle) =>{
                            return(
                                <Marker position={[vehicle.lat,vehicle.lng]}>
                                    <Popup>{vehicle.id}</Popup>
                                </Marker>
                            )
                        })}
                         
                    </Map>
                    </div>

                </div>
            </div>
        )
    }
}


const root = document.getElementById('root');
ReactDOM.render(<Dashboard />, root);