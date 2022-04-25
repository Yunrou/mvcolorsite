import { GET_COLORENCODINGS } from '../actions/types';

const initialState = {
    colorencodings: [],
}

export default function colorencodingsReducer(state=initialState, action) {
    switch(action.type) {
        case GET_COLORENCODINGS:
            return {
                ...state,
                colorencodings: action.payload,
            }
        default:
            return state
    }
}