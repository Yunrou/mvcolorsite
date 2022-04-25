import React, { Component, Fragment, useState } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import { setParam, getParam } from '../../actions/parameters';
import { recolorCharts } from '../../actions/charts';
import { getMVColorEncodings } from '../../actions/mvcolorencodings';
import { getMVConceptGroupings } from '../../actions/mvconceptgroupings';

import InputNumber from './InputNumber';
import MinMaxSlider from './MinMaxSlider'
import Slider from './Slider';
import RecoloringLoader from './RecoloringLoader';

export class Settings extends Component {

    static propTypes = {
        params: PropTypes.array.isRequired,
        mvcolorencodings: PropTypes.array.isRequired,
        mvconceptgroupings: PropTypes.array.isRequired,
        setParam: PropTypes.func.isRequired, 
        recolorCharts: PropTypes.func.isRequired,
    };
    // interactions
    constructor(props) {
        super(props);
        this.state = {
            open: true,
            disabled: false,
            minNColor: 1,
            maxNColor: 9,
            gamma: 0.3,
            setGamma: 0.3,
            key: 0,
            consistency: "visual+semantics",
            selectMVCE: 0,
            selectMVCG: 0,
            recoloring_loader: true,
        }
        this.toggle = this.toggle.bind(this);
        this.handleSelect = this.handleSelect.bind(this);
        this.handleSetMVCE = this.handleSetMVCE.bind(this);
        this.handleRecolor = this.handleRecolor.bind(this);
    }
    componentDidMount() {
        this.props.getParam();
    }
    componentDidUpdate(prevProps, prevStates) {
        if (!this.props.loading && prevProps.loading) {
            console.log("loaded!");
            this.props.getParam();
            this.props.getMVColorEncodings();
            this.props.getMVConceptGroupings();
            if(this.timeout) clearTimeout(this.timeout);
            this.timeout = setTimeout(function(){
                var setKey = (this.state.key)? 0:1;
                var param = this.props.params[0];
                this.setState({
                  selectMVCE: param.mvce_id,
                  selectMVCG: param.mvcg_pk,
                  consistency: param.consistency,
                  minNColor: param.min_n_color,
                  maxNColor: param.max_n_color,
                  gamma: param.gamma,
                  setGamma: param.gamma,
                  key: setKey
                });
            }.bind(this), 500);
        }
        if (!this.props.recoloring && prevProps.recoloring) {
            console.log("recolored!");
            this.props.getParam();
            if(this.timeout) clearTimeout(this.timeout);
            this.timeout = setTimeout(function(){
                var param = this.props.params[0];
                this.setState({
                  selectMVCE: param.mvce_id,
                  selectMVCG: param.mvcg_pk,
                  gamma: param.gamma,
                  setGamma: param.gamma,
                  recoloring_loader: true
                });
                if (param.consistency != "theme") {
                    this.setState({ consistency: param.consistency })
                }
            }.bind(this), 500);
        } 
    }

    toggle() {
        this.setState({ open: !this.state.open });
    }
    handleSelect(event) {
        const value = event.target.value;
        var mvcg = this.props.mvconceptgroupings.filter(
                    e => ((e.mvce_id == this.state.selectMVCE) && (e.consistency == value))
                )[0];
        const pk = mvcg.id;
        this.setState({ consistency: value,
                        selectMVCG: pk, 
                        recoloring_loader: false });
        var param = this.props.params[0];
        param.mvcg_pk = pk;
        param.consistency = value;
        this.props.recolorCharts(param, "concept_grouping");
    }
    handleSetMVCE(event) {
        const mvce_id = event.target.value;
        var mvcg = this.props.mvconceptgroupings.filter(
                    e => ((e.mvce_id == mvce_id) && (e.mvcg_id == 0))
                )[0];
        const pk = mvcg.id;
        this.setState({ selectMVCE: mvce_id,
                        selectMVCG: pk, 
                        recoloring_loader: false });
        var param = this.props.params[0];
        param.mvcg_pk = pk;
        param.consistency = 'visual+semantics';
        this.props.recolorCharts(param, "concept_grouping");
    }
    handleRecolor(event) {
        const pk = event.target.value;
        var param = this.props.params[0];
        param.mvcg_pk = pk;
        param.consistency = 'visual+semantics';
        this.setState({ selectMVCG: pk, recoloring_loader: false });
        this.props.recolorCharts(param, "concept_grouping");

                    // <div className="param-container">
                    //     <div className="param-title">#Colors</div>
                    //     <MinMaxSlider name="nbcolors" 
                    //             key={"nbcolors"+this.state.key}
                    //             minColor={this.state.minColor}
                    //             maxColor={this.state.maxColor}
                    //             otherParam={this.props.params[0]}/>
                    // </div>
    }

    render() {
        const {recoloring} = this.props;
        let renderAttrName = () => {
          let mvcolorencodings = this.props.mvcolorencodings
          if (typeof mvcolorencodings !== 'undefined') {
            return <div className="param-container">
                        <div className="param-title">MV Color Encodings</div>
                        { mvcolorencodings.map((mvce, i)=>(
                        <button className={"mvce-container"+(this.state.selectMVCE == mvce.mvce_id? " active":"")}
                                value={mvce.mvce_id} key={"mvce_"+mvce.id}
                                onClick={this.handleSetMVCE}>
                            {mvce.name}
                        </button>
                        ))}
                    </div>
            
          }
        }
        return (
            <Fragment>
            <a className={"sideoption collapsible"+(this.props.disabled? " disabled": "")}
               onClick={this.toggle.bind(this)}>Recommendation</a>
            <div id="setting-panel" className={"sidepanel-collapse"+(this.state.open && !this.props.disabled? " in": "")}>
                <div className="settings-container">
                    {renderAttrName()}
                    <div className="param-container">
                        <div className="param-title">View Grouping</div>
                        <select value={this.state.consistency} onChange={this.handleSelect} 
                                className="selection-box">
                            <option value="visual+semantics">visual+semantics</option>
                            <option value="visual">visual</option>
                            <option value="semantics">semantics</option>
                        </select>
                        <div className="recommendation-container">
                            { this.props.mvconceptgroupings.filter(
                                    e => ((e.mvce_id == this.state.selectMVCE) && 
                                          (e.consistency == this.state.consistency))
                             ).map((mvcg)=>(
                            <button className={"mvcg-container"+(this.state.selectMVCG == mvcg.id? " active":"")}
                                    value={mvcg.id} key={"mvcg_"+mvcg.id}
                                    onClick={this.handleRecolor}>
                                {mvcg.name}
                            </button>
                            ))}
                        </div>
                    </div>
                    

                    <div className="param-container">
                        <div className="param-title">Color Disriminability</div>
                        <RecoloringLoader show={recoloring && this.state.recoloring_loader} />
                        <Slider name="gamma" 
                                defaultParam={this.state.gamma}
                                key={"gamma_"+this.state.key}
                                otherParam={this.props.params[0]}
                                disabled={this.state.disabled} />
                        <div className="bothside-label-container">
                            <span style={{ textAlign: "left", width:"50%", display: "inline-block" }}>intra</span>
                            <span style={{ textAlign: "right", width:"50%", display: "inline-block" }}>inter</span>
                        </div>
                    </div>
                </div>
            </div> 
            </Fragment>
        );
    }
}
// buff
const mapStateToProps = state => ({
    params: state.paramReducer.params,
    loading: state.chartsReducer.loading,
    recoloring: state.chartsReducer.recoloring,
    mvcolorencodings: state.mvcolorencodingsReducer.mvcolorencodings,
    mvconceptgroupings: state.mvconceptgroupingsReducer.mvconceptgroupings,
}); 
export default connect(
    mapStateToProps,
    { setParam, getParam, recolorCharts, getMVColorEncodings, getMVConceptGroupings }
)(Settings);