import React, { Component, Fragment } from 'react';

export class Loader extends Component {
  render() {
    return (
      <Fragment>
      <div className={"fullscreen-loading"+(this.props.show? " in":"")}> 
        <div className="loader-container">
          <div className="loaded">
            <div className="loader-inner ball-spin-fade-loader">
              <div></div>
              <div></div>
              <div></div>
              <div></div>
              <div></div>
              <div></div>
              <div></div>
              <div></div>
            </div>
          </div>
          <div className="loading-text">Analyzing...</div>
        </div>
      </div>
      </Fragment>
    )
  }
}
export default Loader;