import React, { Component, Fragment } from 'react';
import ReactDOM from 'react-dom';

import Layout from './Layout';

import { Provider } from 'react-redux';
import store from '../store';

class App extends Component {
    render() {
        return (
            <Provider store={store}>
                <Fragment>
                    <Layout />
                </Fragment>
            </Provider>
        );
    }
}

ReactDOM.render(<App />, document.getElementById('app'));