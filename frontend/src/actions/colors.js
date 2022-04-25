import axios from 'axios';

import { GET_COLORS, DELETE_COLOR, ADD_COLOR, SET_COLORS, SWAP_COLORS } from './types';
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = 'csrftoken';
const header = 'Token 778b017b5f7a65ec655b4bf4d31e427eeadb2f4a';

// GET COLORS
export const getColors = () => dispatch => {
    axios.get(`/colors/`)
        .then(res => {
            dispatch({
                type: GET_COLORS,
                payload: res.data
            });
        }).catch(err => console.log(err))
}
// DELETE COLOR
export const deleteColor = (id) => dispatch => {
    axios.delete(`/colors/${id}/`)
        .then(res => {
            dispatch({
                type: DELETE_COLOR,
                payload: id
            });
        }).catch(err => console.log(err))
}
// ADD COLOR
export const addColor = (color) => dispatch => {
    axios.post(`/colors/`, { action: 'addcolor',
                             color: color,
                             colorscheme: 'user' })
        .then(res => {
            dispatch({
                type: ADD_COLOR,
                payload: res.data
            });
        }).catch(err => console.log(err))
}
// SET COLORS
export const setColors = (colorscheme) => dispatch => {
    axios.post(`/colors/`, { action: 'setcolors',
                             colorscheme: colorscheme })
        .then(res => {
            dispatch({
                type: SET_COLORS,
                payload: res.data
            });
        }).catch(err => console.log(err))
}
export const swapColors = (swapPks) => dispatch => {
    axios.post(`/colors/`, { action: 'swapcolors',
                             swapPks: swapPks })
        .then(res => {
            dispatch({
                type: SWAP_COLORS,
                payload: res.data
            });
        }).catch(err => console.log(err))
}