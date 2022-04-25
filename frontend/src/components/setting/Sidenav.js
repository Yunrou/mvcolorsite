import React, { Component, Fragment } from 'react';
import ColorScheme from './ColorScheme';
import Examples from './Examples';
import ManualColoring from './ManualColoring';
import Settings from './Settings';

export class Sidenav extends Component {
    render() {
        return (
            <Fragment>
                <div className="sidenav" id="tabs">

                    <a data-tab="#home" className="nav-logo tablink">Multi-View Coloring</a>
                    
                    <div className="sub-sidenav">
                        <Examples MVcolor={this.props.MVcolor}/>
                        <ManualColoring MVcolor={this.props.MVcolor}/>
                        <ColorScheme disabled={!this.props.MVcolor}/>
                        <Settings disabled={!this.props.MVcolor}/>
                    </div>
                </div>
            </Fragment>
        )
    }
}
export default Sidenav