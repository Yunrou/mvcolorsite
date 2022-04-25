import React, { Component, Fragment } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import { getColors, deleteColor, setColors, swapColors } from '../../actions/colors';
import { getColorSchemes } from '../../actions/colorschemes';
import { swapRangeColors } from '../../actions/rangecolors';

import SaveColorScheme from './SaveColorScheme';
import ColorPickr from './ColorPickr';
import BGColorPickr from './BGColorPickr';
import TextColorPickr from './TextColorPickr';

export class ColorScheme extends Component {
    // access colorschemes
    static propTypes = {
        colorschemes: PropTypes.array.isRequired,
        colors: PropTypes.array.isRequired,
        deleteColor: PropTypes.func.isRequired,
        setColors: PropTypes.func.isRequired,
        swapColors: PropTypes.func.isRequired,
    };
    // interactions
    constructor(props) {
        super(props);
        this.state = {
          open: true,
          checkedItems: [],
          palette: 'tableau10',
        }
        this.handleCheck = this.handleCheck.bind(this);
        this.handleDelete = this.handleDelete.bind(this);
        this.handleSelect = this.handleSelect.bind(this);
        this.handleReset = this.handleReset.bind(this);
        this.handleSwap = this.handleSwap.bind(this);
    }
    componentDidMount() {
        this.props.getColors();
        this.props.getColorSchemes();
        // this.setState({ palette: localStorage.getItem('palette') });
    }
    componentDidUpdate(prevProps, prevStates){
        // localStorage.setItem('palette', this.state.palette);
        if (!this.props.loading && prevProps.loading) {
            this.setState({palette: "tableau10"});
        }
    }
    
    toggle() {
        this.setState({ open: !this.state.open });
    }
    handleCheck(event) {
        var checkedItems = [...this.state.checkedItems]
        var index = checkedItems.indexOf(Number(event.target.value));
        if (index !== -1) {
            // pop
            checkedItems.splice(index, 1);
            this.setState({
                checkedItems: checkedItems
            });
        }
        else {
            // push
            this.setState({
                checkedItems: [...this.state.checkedItems, Number(event.target.value)]
            });
        }
    }
    handleDelete(props) {
        var deleteItems = [...this.state.checkedItems];
        if (deleteItems.length == 0) 
            return;
        else {
            deleteItems.forEach(function(pk) {
                props.deleteColor(pk); 
            });
            // clear checkitems
            this.setState({ checkedItems: [] });
        }
    }
    handleSelect(event) {
        var palette = event.target.value;
        this.setState({palette: palette});
        this.props.setColors(palette);
    }
    handleReset(event) {
        var checkedItems = [...this.state.checkedItems];
        // clear checkitems
        this.setState({ checkedItems: [] });
        checkedItems.forEach(function(pk) {
            document.getElementById("checkbox"+pk).checked = false
        });
        this.props.setColors(this.state.palette);
    }
    handleSwap(event) {
        var checkedItems = [...this.state.checkedItems];
        if (checkedItems.length == 0) 
            return;
        else if (checkedItems.length == 2) {
            var swapPks = [];
            checkedItems.forEach(function(pk) {
                swapPks.push(pk);
            });
            this.props.swapColors(swapPks);
        }
        this.props.swapRangeColors(swapPks);
        // clear checkitems
        this.setState({ checkedItems: [] });
        checkedItems.forEach(function(pk) {
            document.getElementById("checkbox"+pk).checked = false
        });
        // <BGColorPickr/>
        //             <TextColorPickr />
        //             <select value={this.state.palette} onChange={this.handleSelect} 
        //                     name="colorpalette" id="colorpalette">
        //                 { this.props.colorschemes.map(cs => (
        //                     <option key={cs.name} value={cs.name}>{cs.name}</option>    
        //                 ))}
        //             </select>
            // <ColorPickr />
            // <a onClick={()=>this.handleDelete(this.props)} className="color-control" id="color-trash"><i className="fa fa-trash"></i></a>
                    
    }

    render() {
        const {loading} = this.props;
        return (
            <Fragment>
            <a className={"sideoption collapsible"+(this.props.disabled? " disabled": "")}
               onClick={this.toggle.bind(this)}>Color Scheme</a>
                    
            <div id="color-panel" className={"sidepanel-collapse"+(this.state.open && !this.props.disabled? " in": "")}>
                <div className="color-settings-container">
                    <BGColorPickr/>
                    <TextColorPickr />
                    <select value={this.state.palette} onChange={this.handleSelect} 
                            name="colorpalette" id="colorpalette">
                        { this.props.colorschemes.map(cs => (
                            <option key={cs.name} value={cs.name}>{cs.name}</option>    
                        ))}
                    </select>
                    <div className="color-control-container">
                        <ColorPickr />
                        <a onClick={this.handleReset} className="color-control text">Reset</a>
                        <a onClick={this.handleSwap} className="color-control">
                            <i className="fa fa-exchange"></i>
                        </a>
                        <SaveColorScheme />
                        <a onClick={()=>this.handleDelete(this.props)} className="color-control" id="color-trash"><i className="fa fa-trash"></i></a>
                    </div>


                    <div className="color-container">
                        { this.props.colors.map(c => (
                            <label key={c.color} className="color-box-container" for={"checkbox"+c.id} >
                                <input value={c.id} type="checkbox" onChange={this.handleCheck} 
                                       id={"checkbox"+c.id} /> 
                                <span className="checkmark" style={{ backgroundColor: c.color }}></span>
                            </label>
                        ))}
                    </div>
                </div>
            </div>
            </Fragment>
        );
    }
}
// buff
const mapStateToProps = state => ({
    colors: state.colorsReducer.colors,
    colorschemes: state.colorschemesReducer.colorschemes,
    loading: state.chartsReducer.loading
}); 

export default connect(
    mapStateToProps, 
    { getColors, deleteColor, setColors, swapColors, getColorSchemes, swapRangeColors }
)(ColorScheme);