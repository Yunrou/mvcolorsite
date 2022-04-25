import React, { Component, Fragment } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import { saveColorScheme } from '../../actions/colorschemes';

export class SaveColorScheme extends Component {
    
    static propTypes = {
        colors: PropTypes.array.isRequired,
        saveColorScheme: PropTypes.func.isRequired,
    };
    // interactions
    constructor(props) {
        super(props);
        this.state = {
            show: false,
        }
        this.textInput = React.createRef();
        this.toggle = this.toggle.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }
    toggle(event) {
        this.setState({ show: !this.state.show});
    }
    handleSubmit(event) {
        event.preventDefault(); // avoid refresh page
        var customized_name = this.textInput.current.value;
        this.props.saveColorScheme(customized_name);
        this.toggle();
    }
    render() {
        return (
            <Fragment>
            <a onClick={this.toggle} className="color-control">
                <i className="fa fa-save"></i>
            </a>
            <div className={"save-colors-modal"+(this.state.show? " in":"")}> 
                <div className="save-colors-panel">
                    <form onSubmit={this.handleSubmit}>
                        <label>Name</label>
                        <input ref={this.textInput} type="text" />
                        <button type="submit">Save</button>
                    </form>
                </div> 
            </div>
            </Fragment>
        );
    }
}
// buff
const mapStateToProps = state => ({
    colors: state.colorsReducer.colors
}); 

export default connect(
    mapStateToProps, 
    { saveColorScheme }
)(SaveColorScheme);