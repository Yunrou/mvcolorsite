import axios from 'axios';

import { SET_PARAM, GET_PARAM } from './types';
axios.defaults.xsrfHeaderName = "X-CSRFToken"
axios.defaults.xsrfCookieName = 'csrftoken'
const header = 'Token 778b017b5f7a65ec655b4bf4d31e427eeadb2f4a'

// SET PARAMETERS
export const setParam = (param) => dispatch => {
    axios.post(`/parameters/`, {
            param: param,
        })
        .then(res => {
            dispatch({
                type: SET_PARAM,
                payload: res.data
            });
        }).catch(err => console.log(err))
}
export const getParam = () => dispatch => {
    axios.get('/parameters/')
         .then(res => {
            dispatch({
                type: GET_PARAM,
                payload: res.data
            });
         }).catch(err => console.log(err))
}