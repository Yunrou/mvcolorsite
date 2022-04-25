import React, { Component, Fragment, createRef } from 'react';
import { connect } from 'react-redux'
import PropTypes from 'prop-types';
import { setTextColor, getColorConfig } from '../../actions/colorconfig';

import CSRFToken from './Csrftoken';

export class TextColorPickr extends Component { 
    
    static propTypes = {
        colorconfig: PropTypes.array.isRequired,
    };
    constructor(props) {
        super(props);
        this.state = {
          value: '',
        }
    }
    componentDidMount(){
        this.props.getColorConfig();
        const textPickr = Pickr.create({
            el: '#textcolor-picker',
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

        textPickr.on('save', (color, instance) => {
            var c = '#'+color.toHEXA().join('');
            this.setState({value: c});
            this.props.setTextColor(this.state.value);
            textPickr.hide()
        })
    }
    
    render(){
        return(
            <Fragment>
            <div className="colorconfig-container">
                <label className="colorconfig-name">Text color</label>
                <a id="textcolor-picker">
                    { this.props.colorconfig.map(c => (
                        <label key={c.textcolor+'2'} 
                               className="set-colorconfig" 
                               style={{ backgroundColor: c.textcolor }}>
                        </label>
                    ))}
                </a>
            </div>
            </Fragment>
        );
    }

}
// buff
const mapStateToProps = state => ({
    colorconfig: state.colorconfigReducer.colorconfig
}); 
export default connect(
    mapStateToProps,
    { setTextColor, getColorConfig }
)(TextColorPickr);