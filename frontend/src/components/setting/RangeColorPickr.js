import React, { Component, Fragment, createRef } from 'react';
import { connect } from 'react-redux'
import PropTypes from 'prop-types';
import { updateRangeColor } from '../../actions/rangecolors';
import { updateChart } from '../../actions/charts';

export class RangeColorPickr extends Component { 
    
    static propTypes = {
    };
    
    constructor(props) {
        super(props);
        this.state = {
          value: '',
        }
        this.myRef= React.createRef();
    }
    componentDidMount(){
        var swatches = [];
        this.props.colors.forEach(function(color, i) {
            swatches.push(color.color);
        })
        var rangePickr = Pickr.create({
            el: '#rangecolor-pickr'+this.props.rc_pk,
            theme: 'monolith', // or 'monolith', or 'nano'
            useAsButton: true,

            // lockOpacity: false,

            swatches: swatches,

            components: {

                // Main components
                preview: false,
                opacity: false,
                hue: false,

                // Input / output Options
                interaction: {
                    input: false,
                    clear: false,
                    save: true
                }
            }
        });

        rangePickr.on('save', (color, instance) => {
            var c = '#'+color.toHEXA().join('')
            if ((c !== this.state.value) && (c !== '#42445a')) {
                console.log(c);
                this.setState({value: c});
                this.props.updateRangeColor(this.props.rc_pk, c);
            }
            rangePickr.hide()
        }).on('swatchselect', (color, instance) => {
            instance._swatchColors.forEach(function(obj, i) {
                if (color == obj.color) {
                    obj.el.classList.add("pcr-active")
                } else {
                    obj.el.classList.remove("pcr-active")
                }
            })
        })
    }
    componentDidUpdate(prevProps, prevStates){
        if (this.props.hexcolor != prevProps.hexcolor) {
            this.setState({value: this.props.hexcolor});
            this.props.updateChart(this.props.chart_pk, 
                                    "savecolor2vegalite", 
                                    this.props.ce_id);
    
        }
        
        var swatches = [];
        this.props.colors.forEach(function(color, i) {
            swatches.push(color.color);
        })
        var rangePickr = Pickr.create({
            el: '#rangecolor-pickr'+this.props.rc_pk,
            theme: 'monolith', // or 'monolith', or 'nano'
            useAsButton: true,

            // lockOpacity: false,

            swatches: swatches,

            components: {

                // Main components
                preview: false,
                opacity: false,
                hue: false,

                // Input / output Options
                interaction: {
                    input: false,
                    clear: false,
                    save: true
                }
            }
        });

        rangePickr.on('save', (color, instance) => {
            var c = '#'+color.toHEXA().join('')
            if ((c !== this.state.value) && (c !== '#42445a')) {
                console.log(c);
                this.setState({value: c});
                this.props.updateRangeColor(this.props.rc_pk, c);
            }
            rangePickr.hide()
        }).on('swatchselect', (color, instance) => {
            instance._swatchColors.forEach(function(obj, i) {
                if (color == obj.color) {
                    obj.el.classList.add("pcr-active")
                } else {
                    obj.el.classList.remove("pcr-active")
                }
            })
        })
    }
    
    render(){
        return(
            <Fragment>
            <div className="rangecolor-container">
                <a className="rangecolor-pickr"
                   id={"rangecolor-pickr"+this.props.rc_pk}
                   ref={this.myRef}>
                   <div key={this.props.hexcolor+this.props.rc_pk} 
                        className="rangecolor-pickr-buttom" 
                        style={{ backgroundColor: this.props.hexcolor }}>
                    </div>
                </a>
            </div>
            </Fragment>
        );
    }

}
export default connect(
    null,
    { updateChart, updateRangeColor }
)(RangeColorPickr);