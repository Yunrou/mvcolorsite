import React, { Component, Fragment } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import { getCharts} from '../../actions/charts';
import { getColors } from '../../actions/colors';

import EditChart from './EditChart';

export class ManualColoring extends Component {
    // access datasets
    static propTypes = {
        charts: PropTypes.array.isRequired,
        colors: PropTypes.array.isRequired,
    };
    // interactions
    constructor(props) {
        super(props);
        this.state = {
            open: false,
            editChartOpen: -1,
            prevColors: [],
        }
        this.toggle = this.toggle.bind(this);
        this.toggleEditChart = this.toggleEditChart.bind(this);
    }
    componentDidMount() {
        this.props.getCharts();
        this.props.getColors();
    }
    componentDidUpdate(prevProps, prevStates){
        if (!this.props.loading && prevProps.loading) {
            this.props.getCharts();
            this.setState({ editChartOpen: -1});
            return;
        }
    }
    toggle() {
        this.setState({ open: !this.state.open });
    }
    toggleEditChart() {
        var editChartID = event.target.value;
        if (editChartID == this.state.editChartOpen) {
            this.setState({ editChartOpen: -1 });
        }
        else {
            this.setState({ editChartOpen: editChartID });
        }
        console.log("colors",this.props.colors);
    }

    render() {
        const {loading} = this.props;
        return (
            <Fragment>
            <a className="sideoption collapsible"
               onClick={this.toggle.bind(this)}>Manual Coloring</a>
            <div id="manualcoloring-panel" className={"sidepanel-collapse"+(this.state.open? " in": "")}>
                <div className="manualcoloring-container">
                    { this.props.charts.map((chart, i)=>(
                    <div className="editchart-container" key={"editChart_"+i}>
                        <button className="editchart-title" value={i}
                                onClick={this.toggleEditChart.bind(this)}>
                                    {chart.title}
                        </button>
                        <EditChart key={"editchart-"+chart.id}
                                   title={chart.title}
                                   chart_pk={chart.id}
                                   chart_id={chart.index}
                                   ce_id={chart.ce_id}
                                   ce_field={chart.ce_field}
                                   colors={this.props.colors}
                                   open={(this.state.editChartOpen == i)? true:false}
                                   MVcolor={this.props.MVcolor}/>
                    </div>
                    ))}
                </div>
            </div> 
            </Fragment>
        );
    }
}
const mapStateToProps = state => ({
    charts: state.chartsReducer.charts,
    colors: state.colorsReducer.colors,
    loading: state.chartsReducer.loading
}); 
export default connect(
    mapStateToProps, 
    { getCharts, getColors }
)(ManualColoring);