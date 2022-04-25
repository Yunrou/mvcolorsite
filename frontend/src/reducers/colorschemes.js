// take actions
import { GET_COLORSCHEMES, SAVE_COLORSCHEME } from '../actions/types.js';

const initialState = {
    colorschemes: []
}

export default function colorschemesReducer(state=initialState, action) {
    switch(action.type) {
        case SAVE_COLORSCHEME:
            return {
                ...state,
                colorschemes: action.payload,
            };
        case GET_COLORSCHEMES:
            return {
                ...state,
                colorschemes: action.payload,
            };
        default:
            return state;
    }
}