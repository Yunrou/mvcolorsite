import axios from 'axios';
import { GET_CHARTS, ADD_CHARTS, DELETE_CHART, UPDATE_CHART, SET_EDIT_COLORENCODING, RECOLORING_CHARTS, RECOLORED_CHARTS, LOADING_EXAMPLE, LOADED_EXAMPLE } from './types';

export const getCharts = () => dispatch => {
    axios.get('/charts/')
         .then(res => {
            dispatch({
                type: GET_CHARTS,
                payload: res.data
            });
         }).catch(err => console.log(err))
}

export const addCharts = (formData) => dispatch => {
    axios.post('/charts/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        }).then(res => {
            dispatch({
                type: ADD_CHARTS,
                payload: res.data
            });
        }).catch(err => console.log(err))

}

export const deleteChart = (id) => dispatch => {
    axios.delete(`/charts/${id}/`)
        .then(res => {
            dispatch({
                type: DELETE_CHART,
                payload: id
            });
        }).catch(err => console.log(err))
}
export const updateChart = (id, action, ce_id) => dispatch => {
    axios.put(`/charts/${id}/`, { action: action,
                                  ce_id: ce_id })
        .then(res => {
            dispatch({
                type: UPDATE_CHART,
                payload: res.data
            });
        }).catch(err => console.log(err))
}

export const recolorCharts = (param, cmd) => dispatch => {
    dispatch({ type: RECOLORING_CHARTS}); //Recoloring starts
    axios.post('/charts/', { action: 'recolor',
                             param: param,
                             cmd: cmd })
        .then(res => {
            dispatch({
                type: RECOLORED_CHARTS,
                payload: res.data
            });
        }).catch(err => console.log(err))
}

export const loadExample = (example, MVcolor) => dispatch => {
    dispatch({ type: LOADING_EXAMPLE }); //Loading starts
    axios.post('/charts/', { action: 'load_example',
                             example: example,
                             MVcolor: MVcolor })
        .then(res => {
            dispatch({
                type: LOADED_EXAMPLE,
                payload: res.data
            });
        }).catch(err => console.log(err))
}