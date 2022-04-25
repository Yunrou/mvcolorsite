import { SET_PARAM, GET_PARAM } from '../actions/types';

const initialState = {
    params: []
}

export default function paramReducer(state=initialState, action) {
    switch(action.type) {
        case SET_PARAM:
            return {
                ...state,
                params: action.payload,
            }
        case GET_PARAM:
            return {
                ...state,
                params: action.payload,
            }
        default:
            return state
    }
}