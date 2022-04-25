import axios from 'axios';

import { GET_EXAMPLES } from './types';
axios.defaults.xsrfHeaderName = "X-CSRFToken"
axios.defaults.xsrfCookieName = 'csrftoken'
const header = 'Token 778b017b5f7a65ec655b4bf4d31e427eeadb2f4a'

// GET EXAMPLES
export const getExamples = () => dispatch => {
    axios.get('/examples/')
         .then(res => {
            dispatch({
                type: GET_EXAMPLES,
                payload: res.data
            });
         }).catch(err => console.log(err))
}