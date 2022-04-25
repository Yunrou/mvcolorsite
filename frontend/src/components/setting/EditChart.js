import React, { Component, Fragment } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import { updateChart } from '../../actions/charts';
import { getColorEncodings } from '../../actions/colorencodings';
import { getRangeColors } from '../../actions/rangecolors';

import RangeColorPickr from './RangeColorPickr';

export class EditChart extends Component {
    static propTypes = {
        colorencodings: PropTypes.array.isRequired,
        rangecolors: PropTypes.array.isRequired
    };
    constructor(props) {
        super(props);
        this.state = {
            field: this.props.ce_field,
            ce_id: 0,
        }
        this.handleSelect = this.handleSelect.bind(this);
    }

    componentDidMount() {
        this.props.getColorEncodings();
        this.props.getRangeColors();
        this.setState({ ce_id: this.props.ce_id })
    }
    componentDidUpdate(prevProps, prevStates){
        // localStorage.setItem('ce_id', this.state.ce_id);
        if (!this.props.recoloring && prevProps.recoloring) {
            this.props.getColorEncodings();
            this.props.getRangeColors();
            this.setState({ce_id: this.props.ce_id});
            return;
        }
        if (!this.props.loading && prevProps.loading) {
            this.props.getColorEncodings();
            this.props.getRangeColors();
            this.setState({ce_id: 0});
            // this.props.updateChart(this.props.chart_pk, "set-ce", ce_id);
            // console.log("reset ce id")
            return;
        }
    }
    handleSelect(event) {
        event.preventDefault();
        var ce_id = event.target.value;
        this.setState({ce_id: ce_id})
        console.log("pk", this.props.chart_pk);
        this.props.updateChart(this.props.chart_pk, "set-ce", ce_id);
    }

    render() {
        let {loading} = this.props;

        let renderAttrName = () => {
          let colorencodings = this.props.colorencodings.filter(
                                     e => e.chart_id === this.props.chart_id
                                   )
          if (typeof colorencodings !== 'undefined') {
            if (this.props.MVcolor)
            {
              return (null);
            }
            else if (colorencodings.length == 1 && colorencodings[0].field != "constant") 
            {
              return <div>{colorencodings[0].field}</div>;
            }
            else if (colorencodings.length > 1) 
            {
              return <select id={"selectcolor_"+this.props.chart_pk}
                        value={this.state.ce_id}
                        onChange={this.handleSelect}
                        name="color-encoding">
                        { colorencodings.filter(
                            e => e.chart_id === this.props.chart_id
                        ).map((ce) => (
                          <option key={"selectcolor_"+ce.ce_id}
                                  id={"selectcolor_"+ce.ce_id}
                                  value={ce.ce_id}>
                                  {ce.name}
                          </option>
                        ))};
                    </select>
            }
          } else {
            return (null);
          } 
        }
        return (
            <Fragment>
            <div className={"editchart-panel-collapse"+(this.props.open? " in": "")}>
                {renderAttrName()}
                { this.props.colorencodings.filter(
                    ce => (ce.chart_id === this.props.chart_id) &&
                        (ce.ce_id === this.props.ce_id)
                  ).map(ce => (
                    <div key={"domain_"+ce.chart_id+"_"+ce.ce_id}>
                        <div className="colormap-container">
                            <div className="rangecolors-container">
                            { this.props.rangecolors.filter(
                                rc => (rc.chart_id === this.props.chart_id) &&
                                     (rc.ce_id === this.props.ce_id)
                              ).map(rc => (
                                <div key={"colorconcept"+rc.id} className="colorconcept-container">
                                    <RangeColorPickr 
                                        key={"rangecolorpickr"+rc.id}
                                        rc_pk={rc.id}
                                        concept={rc.concept}
                                        hexcolor={rc.hexcolor}
                                        colors={this.props.colors}
                                        chart_pk={this.props.chart_pk}
                                        ce_id={this.props.ce_id}/>

                                    <div className="concept">{rc.concept}</div>
                                </div>
                            ))}
                            </div>
                            
                        </div>  
                    </div>
                ))}
            </div>
            </Fragment>
        )
    }
}
// buff
const mapStateToProps = state => ({
    colorencodings: state.colorencodingsReducer.colorencodings,
    rangecolors: state.rangecolorsReducer.rangecolors,
    recoloring: state.chartsReducer.recoloring,
    loading: state.chartsReducer.loading
}); 

export default connect(
    mapStateToProps, 
    { updateChart, getColorEncodings, getRangeColors }
)(EditChart);