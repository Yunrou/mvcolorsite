import { GET_RANGECOLORS, UPDATE_RANGECOLOR, SWAP_RANGECOLORS } from '../actions/types';

const initialState = {
    rangecolors: []
}

export default function rangecolorsReducer(state=initialState, action) {
    switch(action.type) {
        case GET_RANGECOLORS:
            return {
                ...state,
                rangecolors: action.payload,
            }
        case UPDATE_RANGECOLOR:
            return {
                ...state,
                rangecolors: action.payload,
            }
        case SWAP_RANGECOLORS:
            return {
                ...state,
                rangecolors: action.payload,
            }
        default:
            return state
    }
}