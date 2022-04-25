import React, { Component, Fragment } from 'react';

import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import { setParam } from '../../actions/parameters';
import { recolorCharts } from '../../actions/charts';

export class Slider extends Component {
  static propTypes = {
    setParam: PropTypes.func.isRequired, 
    recolorCharts: PropTypes.func.isRequired,
  };
  constructor(props) {
    super(props);
    this.state = { 
        param: this.props.defaultParam,
        show: false,
        colored_mvcg_pk: -1,
        colored_gamma: -1

    };
    this.handleChange = this.handleChange.bind(this);
    this.handleInput = this.handleInput.bind(this);
    this.handleMouseUp = this.handleMouseUp.bind(this);
  }

  handleInput(event) {
    const value = parseFloat(event.target.value);
    this.setState({ show: true, param: value });
  }
  handleChange(event) {
    // const value = parseFloat(event.target.value);
    // this.setState({ show: true, param: value });
  }
  handleMouseUp(event) {
    // event.preventDefault();
    const value = parseFloat(event.target.value);
    this.setState({ show: false });
    var param = this.props.otherParam;
    var change = false
    var colorAssignment = true
    if (this.props.name == 'gamma') {
      if (param.gamma !== value) {
        param.gamma = value;
        change = true;
      }
      // if (param.isTheme) {
      //   colorAssignment = false
      // }
      // if ((this.state.colored_mvcg_pk == param.mvcg_pk)
      //     && (this.state.colored_gamma == value)) {
      //   colorAssignment = false
      // }
    }
    console.log("Click", change, colorAssignment)
    if (change) {
      this.props.setParam(param);  
    }
    if (colorAssignment) {
      this.props.recolorCharts(param, "color_assignment");
      this.setState({ colored_mvcg_pk: param.mvcg_pk, 
                      colored_gamma: value })  
    }
    
    // <div className={"slider-bubble"+(this.state.show? " in" : "")}
    //      style={{left: (this.state.param*10-0.5) +'vw'}}>
    //      <span className="bubble-value">{this.state.param}</span>
    //      <i className="fa fa-map-marker"></i>
    // </div>
  }
  render() {
    return (
      <Fragment>
      <div className="slider-parent">
          <input name={this.props.name}
                 className="slider" type="range" 
                 min="0" max="1" step="0.1"
                 value={this.state.param}
                 onInput={this.handleInput}
                 onChange={this.handleChange}
                 onMouseUp={this.handleMouseUp}
                 disabled = {(this.props.disabled)? "disabled" : ""}/>
          <svg className="slider-ticks" role="presentation" height="8">
              <rect className="range-tick" x="0%" y="3" width="1" height="6"></rect>
              <rect className="range-tick" x="9%" y="3" width="1" height="6"></rect>
              <rect className="range-tick" x="18%" y="3" width="1" height="6"></rect>
              <rect className="range-tick" x="27%" y="3" width="1" height="6"></rect>
              <rect className="range-tick" x="36%" y="3" width="1" height="6"></rect>
              <rect className="range-tick" x="45%" y="3" width="1" height="6"></rect>
              <rect className="range-tick" x="54%" y="3" width="1" height="6"></rect>
              <rect className="range-tick" x="63%" y="3" width="1" height="6"></rect>
              <rect className="range-tick" x="72%" y="3" width="1" height="6"></rect>
              <rect className="range-tick" x="81%" y="3" width="1" height="6"></rect>
              <rect className="range-tick" x="90%" y="3" width="1" height="6"></rect>
          </svg>
        </div>
      </Fragment>
    )
  }
}
export default connect(
    null,
    { setParam, recolorCharts }
)(Slider);