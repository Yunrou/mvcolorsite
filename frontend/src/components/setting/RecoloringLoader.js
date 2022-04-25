import React, { Component, Fragment } from 'react';

export class RecoloringLoader extends Component {
  render() {
    return (
      <Fragment>
      <div className={"recoloring-loader"+(this.props.show? " in":"")}> 
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
        </div>
      </div>
      </Fragment>
    )
  }
}
export default RecoloringLoader;