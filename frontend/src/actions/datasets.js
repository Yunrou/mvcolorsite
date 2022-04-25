import axios from 'axios';

import { GET_DATASETS, ADD_DATASETS } from './types';

// GET DATASETS
export const getDatasets = () => dispatch => {
    axios.get('/datasets/')
        .then(res => {
            dispatch({
                type: GET_DATASETS,
                payload: res.data
            });
        }).catch(err => console.log(err))
}

// ADD DATASETS
export const addDatasets = (formData) => dispatch => {
    axios.post('/datasets/', formData, {   
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        .then(res => {
            dispatch({
                type: ADD_DATASETS,
                payload: res.data
            });
        }).catch(err => console.log(err))
}
