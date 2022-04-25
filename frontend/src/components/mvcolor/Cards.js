import React, { Component, Fragment, PureComponent } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import RGL, { WidthProvider } from "react-grid-layout";
const ReactGridLayout = WidthProvider(RGL);

const originalLayout = getFromLS("layout") || [];

import Card from './Card';
import { getCharts } from '../../actions/charts';
import { getColorConfig } from '../../actions/colorconfig';

export class Cards extends PureComponent {
    static propTypes = {
        charts: PropTypes.array.isRequired,
        colorconfig: PropTypes.array.isRequired,
    };
    static defaultProps = {
        className: "layout",
        cols: 24,
        rowHeight: 23,
        onLayoutChange: function() {}
    };
    constructor (props) {
        super(props);
        this.state = {
            show: false,
            layout: JSON.parse(JSON.stringify(originalLayout)),
            bgcolor: "#fff",
            textcolor: "#333",
        };
        this.toggle = this.toggle.bind(this);
        this.onLayoutChange = this.onLayoutChange.bind(this);
    }
    componentDidMount() {
        this.props.getCharts();
        this.props.getColorConfig();
        this.setState({ layout: JSON.parse(JSON.stringify(originalLayout)) });
        var config = this.props.colorconfig;
        if (config.length != 0) {
            this.setState({ 
                bgcolor: config[0].bgcolor,
                textcolor: config[0].textcolor
            });
        }
    }
    componentDidUpdate(prevProps, prevStates) {
        saveToLS("layout", this.state.layout);
        var config = this.props.colorconfig;
        if (config.length != 0) {
            this.setState({ 
                bgcolor: config[0].bgcolor,
                textcolor: config[0].textcolor
            });
        }
    }
    onLayoutChange(layout) {
        saveToLS("layout", layout);
        this.setState({ layout });
        // this.props.onLayoutChange(layout);
    }
    toggle() {
        this.setState({ show: !this.state.show });
    }
    
    render() {
        return (
            <Fragment>
            <ReactGridLayout {...this.props}
                             layout={JSON.parse(JSON.stringify(getFromLS("layout")||[]))}
                             onLayoutChange={this.onLayoutChange}>
                
            { this.props.charts.map((chart, i)=>(
            <div className="card" 
                 style={{ backgroundColor: this.state.bgcolor }} 
                 key={"chart_"+chart.id} data-grid={{x: chart.x, 
                                                     y: chart.y, 
                                                     w: chart.w, 
                                                     h: chart.h, 
                                                     static: true}}>
                <div className="card-header">
                    <div className="card-title" 
                         style={{ color: this.state.textcolor }}>
                         {chart.title}
                    </div>
                </div>
                <div className="card-main">
                    <div className="chart-container">
                        <div className="chart" id={"chart_"+chart.id}></div>
                    </div>
                </div>
                <Card spec={chart.spec}
                      pk={chart.id} 
                      bgcolor={this.state.bgcolor}
                      textcolor={this.state.textcolor}/>
            </div>
            ))}
            </ReactGridLayout>
            </Fragment>
        )
    }
}
const mapStateToProps = state => ({
    charts: state.chartsReducer.charts,
    colorconfig: state.colorconfigReducer.colorconfig
}); 

export default connect (
    mapStateToProps,
    { getCharts, getColorConfig }
)(Cards);


function getFromLS(key) {
  let ls = {};
  if (global.localStorage) {
    try {
      ls = JSON.parse(global.localStorage.getItem("rgl-7")) || {};
    } catch (e) {
      /*Ignore*/
    }
  }
  return ls[key];
}

function saveToLS(key, value) {
  if (global.localStorage) {
    global.localStorage.setItem(
      "rgl-7",
      JSON.stringify({
        [key]: value
      })
    );
  }
}