import { GET_EXAMPLES } from '../actions/types';

const initialState = {
    examples: []
}

export default function examplesReducer(state=initialState, action) {
    switch(action.type) {
        case GET_EXAMPLES:
            return {
                ...state,
                examples: action.payload,
            }
        default:
            return state
    }
}