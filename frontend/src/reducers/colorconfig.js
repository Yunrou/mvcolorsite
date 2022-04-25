// take actions
import { GET_COLORCONFIG, SET_BGCOLOR, SET_TEXTCOLOR } from '../actions/types.js';

const initialState = {
    colorconfig: []
}

export default function colorconfigReducer(state=initialState, action) {
    switch(action.type) {
        case GET_COLORCONFIG:
            return {
                ...state,
                colorconfig: action.payload,
            };
        case SET_BGCOLOR:
            return {
                ...state,
                colorconfig: action.payload,
            };
        case SET_TEXTCOLOR:
            return {
                ...state,
                colorconfig: action.payload,
            };
        default:
            return state;
    }
}