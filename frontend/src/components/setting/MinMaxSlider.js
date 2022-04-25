import React, { Component, Fragment } from 'react';
import { useState, useEffect, useLayoutEffect } from "react";
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import { setParam } from '../../actions/parameters';
import { recolorCharts } from '../../actions/charts';

import MultiRangeSlider from './MultiRangeSlider'

export class MinMaxSlider extends Component {
  

  static propTypes = {
    setParam: PropTypes.func.isRequired, 
    recolorCharts: PropTypes.func.isRequired,
  };
  constructor(props) {
    super(props);
    this.state = { 
        minColor: this.props.minColor,
        maxColor: this.props.maxColor,
    };
  }
  render() {
    return (
      <Fragment>
      <MultiRangeSlider
          min={this.props.minColor}
          max={this.props.maxColor}
          rangeMin={1}
          rangeMax={10}
          mouseup={false}
          onMouseUp={({ min, max }) => {
            
            var param = this.props.otherParam;
            if (typeof param !== 'undefined') {
                var recolor = false;
                var minColor = Math.min(min, max);
                var maxColor = Math.max(min, max);
                if (this.state.minColor !== minColor) {
                    this.setState({ minColor: minColor });
                    recolor = true;
                }
                else if (this.state.maxColor !== maxColor) {
                    this.setState({ maxColor: maxColor });
                    recolor = true
                }
                if (recolor) {
                    param.min_color = minColor;
                    param.max_color = maxColor;
                    this.props.setParam(param);
                    this.props.recolorCharts(param);
                }
            }
            
          }}
        />
      </Fragment>
    )
  }
}
export default connect(
    null,
    { setParam, recolorCharts }
)(MinMaxSlider);