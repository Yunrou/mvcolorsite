import axios from 'axios';

import { GET_MVCONCEPTGROUPINGS } from './types';
axios.defaults.xsrfHeaderName = "X-CSRFToken"
axios.defaults.xsrfCookieName = 'csrftoken'
const header = 'Token 778b017b5f7a65ec655b4bf4d31e427eeadb2f4a'

// GET MVCONCEPTGROUPINGS
export const getMVConceptGroupings = () => dispatch => {
    axios.get('/mvconceptgroupings/')
         .then(res => {
            dispatch({
                type: GET_MVCONCEPTGROUPINGS,
                payload: res.data
            });
         }).catch(err => console.log(err))
}