import { GET_MVCONCEPTGROUPINGS } from '../actions/types';

const initialState = {
    mvconceptgroupings: []
}

export default function mvconceptgroupingsReducer(state=initialState, action) {
    switch(action.type) {
        case GET_MVCONCEPTGROUPINGS:
            return {
                ...state,
                mvconceptgroupings: action.payload,
            }
        default:
            return state
    }
}