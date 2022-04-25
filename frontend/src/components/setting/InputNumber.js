import React, { Component, Fragment } from 'react';

import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import { setParam } from '../../actions/parameters';
import { recolorCharts } from '../../actions/charts';

export class InputNumber extends Component {
  static propTypes = {
    setParam: PropTypes.func.isRequired, 
  };
  constructor(props) {
    super(props);
    this.state = { param: this.props.defaultParam };
    this.param = React.createRef();
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleSubmit(event) {
    const value = parseInt(this.param.current.value)
    this.setState({ param: value });
    // set param and recolor
    var param = this.props.otherParam;
    param.alpha = value
    console.log("Submit", param)
    this.props.setParam(param);
    this.props.recolorCharts(param);
  };
  render() {
    return (
      <Fragment>
      <form onSubmit={this.handleSubmit}>
        <input name={this.props.name} ref={this.param} type="number" 
               min="1" max="10" value={this.state.param}
               onInput={this.handleSubmit}
               disabled = {(this.props.disabled)? "disabled" : ""}/>
        <button type="submit">Save</button>
      </form>
      </Fragment>
    )
  }
}

export default connect(
    null,
    { setParam, recolorCharts }
)(InputNumber);