import { GET_MVCOLORENCODINGS } from '../actions/types';

const initialState = {
    mvcolorencodings: []
}

export default function mvcolorencodingsReducer(state=initialState, action) {
    switch(action.type) {
        case GET_MVCOLORENCODINGS:
            return {
                ...state,
                mvcolorencodings: action.payload,
            }
        default:
            return state
    }
}