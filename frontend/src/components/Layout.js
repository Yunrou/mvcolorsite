import React, { Component, Fragment } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import html2canvas from 'html2canvas'

import Sidenav from './setting/Sidenav';
import RecoloringLoader from './setting/RecoloringLoader';
import Cards from './mvcolor/Cards';

import { getParam } from '../actions/parameters';
import { recolorCharts } from '../actions/charts';
import { getExamples } from '../actions/examples';

export class Layout extends Component {
    static propTypes = {
        params: PropTypes.array.isRequired,
        getParam: PropTypes.func.isRequired, 
        examples: PropTypes.array.isRequired,
    };
    constructor(props) {
        super(props);
        this.state = {
            show: false,
            MVcolor: false // disable MVcolor recommendation
        }
        this.componentRef = React.createRef();
        this.handleClick = this.handleClick.bind(this);
        this.handleToggle = this.handleToggle.bind(this);
        this.handleScreenShot = this.handleScreenShot.bind(this);
        this.handleRecolor = this.handleRecolor.bind(this);
    }
    componentDidMount() {
        this.props.getExamples();
        // this.setState({ MVcolor: localStorage.getItem('MVcolor') });
    };
    componentDidUpdate(prevProps, prevStates) {
        // localStorage.setItem('MVcolor', this.state.MVcolor);
        if (!this.props.loading && prevProps.loading) {
            this.props.getExamples();
        }
    };

    handleClick(event) {
        this.setState({ show: !this.state.show })
    }

    handleToggle(event) {
        this.setState({ MVcolor: !this.state.MVcolor });
        this.setState({ show: false });
    }
    handleScreenShot(event) {
        this.setState({ show: false });
        const captureElement = document.querySelector('#dashboard')
        html2canvas(captureElement)
        .then(canvas => {
            canvas.style.display = 'none'
            document.body.appendChild(canvas)
            return canvas
        })
        .then(canvas => {
            const image = canvas.toDataURL('image/png').replace('image/png', 'image/octet-stream')
            const a = document.createElement('a')
            a.setAttribute('download', 'mv.png')
            a.setAttribute('href', image)
            a.click()
            canvas.remove()
        })
    }

    handleRecolor(event) {
        console.log("recolor");
        var param = this.props.params[0];
        this.props.recolorCharts(param, "default");
    };
    render() {
        const {loading} = this.props;
        const {recoloring} = this.props;
        return (
            <Fragment>
                <Sidenav key="sidenav" MVcolor={this.state.MVcolor}/>
                <div className="header">
                    <a onClick={this.handleClick} className="header-option">
                        <i className="fa fa-bars"></i>
                    </a>
                    <div className={"header-option-modal"+(this.state.show? " in": "")}>
                        <div className="option-container">
                            <div className="option">MVcolor</div>
                            <div className={"toggle-switch"+(this.state.MVcolor? " active": "")} 
                                 onClick={this.handleToggle}>
                                <div className={"knob"+(this.state.MVcolor? "": " active")}></div>
                            </div>
                        </div>
                        <div className="option-container">
                            <div className="option">Export MV</div>
                            <a class="screenshot" onClick={this.handleScreenShot}>
                                <i className="fa fa-download"></i>
                            </a>
                        </div>
                    </div>
                    <a onClick={this.handleRecolor} 
                       className={"action"+(this.state.MVcolor? "": " disabled")}>
                        <div className="recolor">Color!</div>
                    </a>
                    {this.props.examples.filter(
                         e => (e.current === true)
                    ).map((e) => (
                        <div className="example-title" key="title">{e.name.substring(2, e.name.length)}</div>
                    ))}
                </div>
                <div className="tab-content">
                    <div className="tab-pane" id="dashboard">
                        <div className="main"><Cards /></div>
                    </div>
                </div>
            </Fragment>
        );    
    }
}
const mapStateToProps = state => ({
    params: state.paramReducer.params,
    loading: state.chartsReducer.loading,
    examples: state.examplesReducer.examples,
    recoloring: state.chartsReducer.recoloring
}); 
export default connect (
    mapStateToProps,
    { getParam, recolorCharts, getExamples }
)(Layout);