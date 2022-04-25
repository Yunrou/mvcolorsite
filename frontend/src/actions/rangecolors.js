import axios from 'axios';
import { GET_RANGECOLORS, UPDATE_RANGECOLOR, SWAP_RANGECOLORS } from './types';

export const getRangeColors = () => dispatch => {
    axios.get('/rangecolors/')
         .then(res => {
            dispatch({
                type: GET_RANGECOLORS,
                payload: res.data
            });
         }).catch(err => console.log(err))
}

export const updateRangeColor = (id, hexcolor) => dispatch => {
    axios.put(`/rangecolors/${id}/`, { hexcolor: hexcolor })
        .then(res => {
            dispatch({
                type: UPDATE_RANGECOLOR,
                payload: res.data
            });
        }).catch(err => console.log(err))
}
export const swapRangeColors = (swapPks) => dispatch => {
    axios.post(`/rangecolors/`, { action: 'swap',
                                  swapPks: swapPks })
        .then(res => {
            dispatch({
                type: SWAP_RANGECOLORS,
                payload: res.data
            });
        }).catch(err => console.log(err))
}