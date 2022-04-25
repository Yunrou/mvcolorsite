import React, { Component, Fragment, createRef } from 'react';
import { connect } from 'react-redux'
import PropTypes from 'prop-types';
import { addColor } from '../../actions/colors';

import CSRFToken from './Csrftoken';

export class ColorPickr extends Component { 

    componentDidMount(){
        const pickr = Pickr.create({
            el: '#color-picker',
            theme: 'classic', // or 'monolith', or 'nano'
            useAsButton: true,
            // lockOpacity: false,

            swatches: [
                'rgb(244, 67, 54)',
                'rgb(233, 30, 99)',
                'rgb(156, 39, 176)',
                'rgb(103, 58, 183)',
                'rgb(63, 81, 181)',
                'rgb(33, 150, 243)',
                'rgb(3, 169, 244)',
                'rgb(0, 188, 212)',
                'rgb(0, 150, 136)',
                'rgb(76, 175, 80)',
                'rgb(139, 195, 74)',
                'rgb(205, 220, 57)',
                'rgb(255, 235, 59)',
                'rgb(255, 193, 7)'
            ],

            components: {

                // Main components
                preview: true,
                opacity: false,
                hue: true,

                // Input / output Options
                interaction: {
                    hex: true,
                    rgba: true,
                    hsla: true,
                    hsva: true,
                    cmyk: true,
                    input: true,
                    clear: false,
                    save: true
                }
            }
        });

        pickr.on('save', (color, instance) => {
            var c = '#'+color.toHEXA().join('');
            this.setState({value: c});
            this.props.addColor(this.state.value);
            pickr.hide();
        })
    } 
    constructor(props) {
        super(props);
        this.state = {
          value: '',
        }
    }
    
    render(){
        return(
            <Fragment>
            <a id="color-picker" className="color-control color-picker"><i className="fa fa-plus"></i></a>
            </Fragment>
        );
    }

}
export default connect(
    null,
    { addColor }
)(ColorPickr);