import React, { Component, Fragment } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import { getCharts, deleteChart } from '../../actions/charts';

export class DeleteCard extends Component {
    constructor(props) {
        super(props);
        this.handleDelete = this.handleDelete.bind(this);
    }
    handleDelete(event) {
        var pk = Number(event.target.id.split("_")[1])
        this.props.deleteChart(pk);
    }
    render() {
        return (
            <Fragment>
            <a id={"deletecard_"+this.props.id} onClick={this.handleDelete} className="card-control-option">Delete</a>
            </Fragment>
        )
    }
}
export default connect (
    null,
    { deleteChart }
)(DeleteCard);