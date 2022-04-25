import axios from 'axios';

import { GET_COLORENCODINGS } from './types';
axios.defaults.xsrfHeaderName = "X-CSRFToken"
axios.defaults.xsrfCookieName = 'csrftoken'
const header = 'Token 778b017b5f7a65ec655b4bf4d31e427eeadb2f4a'

export const getColorEncodings = () => dispatch => {
    axios.get('/colorencodings/')
         .then(res => {
            dispatch({
                type: GET_COLORENCODINGS,
                payload: res.data
            });
         }).catch(err => console.log(err))
}