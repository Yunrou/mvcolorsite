// take actions
import { GET_COLORS, DELETE_COLOR, ADD_COLOR, SET_COLORS, SWAP_COLORS } from '../actions/types.js';

const initialState = {
    colors: []
}

export default function colorsReducer(state=initialState, action) {
    switch(action.type) {
        case GET_COLORS:
            return {
                ...state,
                colors: action.payload,
            };
        case DELETE_COLOR:
            return {
                ...state,
                colors: state.colors.filter(color => color.id !== action.payload),
            };
        case ADD_COLOR:
            return {
                ...state,
                colors: action.payload
            };
        case SET_COLORS:
            return {
                ...state,
                colors: action.payload,
            };
        case SWAP_COLORS:
            return {
                ...state,
                colors: action.payload,
            };
        default:
            return state;
    }
}