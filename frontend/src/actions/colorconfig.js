import axios from 'axios';

import { GET_COLORCONFIG, SET_BGCOLOR, SET_TEXTCOLOR } from './types';
axios.defaults.xsrfHeaderName = "X-CSRFToken"
axios.defaults.xsrfCookieName = 'csrftoken'
const header = 'Token 778b017b5f7a65ec655b4bf4d31e427eeadb2f4a'

// GET COLORCONFIG
export const getColorConfig = () => dispatch => {
    axios.get(`/colorconfig/`)
        .then(res => {
            dispatch({
                type: GET_COLORCONFIG,
                payload: res.data
            });
        }).catch(err => console.log(err))
}
// SET BGCOLOR
export const setBGColor = (bgcolor) => dispatch => {
    axios.post(`/colorconfig/`, {
            bgcolor: bgcolor
        })
        .then(res => {
            dispatch({
                type: SET_BGCOLOR,
                payload: res.data
            });
        }).catch(err => console.log(err))
}
// SET TEXTCOLOR
export const setTextColor = (textcolor) => dispatch => {
    axios.post(`/colorconfig/`, {
            textcolor: textcolor
        })
        .then(res => {
            dispatch({
                type: SET_TEXTCOLOR,
                payload: res.data
            });
        }).catch(err => console.log(err))
}