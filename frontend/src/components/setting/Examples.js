import React, { Component, Fragment } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import { loadExample } from '../../actions/charts';
import { getExamples } from '../../actions/examples';
import { setColors } from '../../actions/colors';

import Loader from './Loader';

export class Examples extends Component {
    // access datasets
    static propTypes = {
        examples: PropTypes.array.isRequired,
        loadExample: PropTypes.func.isRequired,
    };
    // interactions
    constructor(props) {
        super(props);
        this.state = {
            open: false,
            example: '',
            loading: false,
        }
        this.toggle = this.toggle.bind(this);
        this.handleClick = this.handleClick.bind(this);
    }
    componentDidMount() {
        this.props.getExamples();
        this.setState({ example: localStorage.getItem('example') });
    }
    componentDidUpdate(prevProps, prevStates){
        localStorage.setItem('example', this.state.example);
    }
    toggle() {
        this.setState({ open: !this.state.open });
    }
    handleClick() {
        this.setState({ open: !this.state.open });
        var example = event.target.value;
        this.setState({example: example})
        this.props.setColors("tableau10");
        this.props.loadExample(example, this.props.MVcolor);
    }

    render() {
        const {loading} = this.props;
        return (
            <Fragment>
            <Loader show={loading} />
            <a className="sideoption collapsible" onClick={this.toggle.bind(this)}>MV Examples</a>
            <div id="example-panel" className={"sidepanel-collapse"+(this.state.open? " in": "")}>
                <div className="examples-container">
                    { this.props.examples.map((example, i)=>(
                    <button className="example-container" 
                            value={example.value} key={"example_"+example.id}
                            onClick={this.handleClick}>
                        {example.name.substring(2, example.name.length)}
                    </button>
                    ))}
                </div>
            </div> 
            </Fragment>
        );
    }
}
const mapStateToProps = state => ({
    loading: state.chartsReducer.loading,
    examples: state.examplesReducer.examples
}); 
export default connect(
    mapStateToProps, 
    { loadExample, getExamples, setColors }
)(Examples);