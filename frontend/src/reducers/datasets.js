import { GET_DATASETS, ADD_DATASETS } from '../actions/types';

const initialState = {
    datasets: []
}

export default function datasetsReducer(state=initialState, action) {
    switch(action.type) {
        case GET_DATASETS:
            return {
                ...state,
                datasets: action.payload,
            }
        case ADD_DATASETS:
            return {
                ...state,
                datasets: action.payload,
            }
        default:
            return state
    }
}
