import axios from 'axios';

import { GET_COLORSCHEMES, SAVE_COLORSCHEME } from './types';
axios.defaults.xsrfHeaderName = "X-CSRFToken"
axios.defaults.xsrfCookieName = 'csrftoken'
const header = 'Token 778b017b5f7a65ec655b4bf4d31e427eeadb2f4a'

// SAVE COLORSCHEME 
export const saveColorScheme = (name) => dispatch => {
    axios.post(`/colorschemes/`, {
            customized_name: name
        })
        .then(res => {
            dispatch({
                type: SAVE_COLORSCHEME,
                payload: res.data
            });
        }).catch(err => console.log(err))
}
// GET COLORSCHEMES
export const getColorSchemes = () => dispatch => {
    axios.get(`/colorschemes/`)
        .then(res => {
            dispatch({
                type: GET_COLORSCHEMES,
                payload: res.data
            });
        }).catch(err => console.log(err))
}