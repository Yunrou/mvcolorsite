import { GET_CHARTS, ADD_CHARTS, DELETE_CHART, UPDATE_CHART, RECOLORING_CHARTS, RECOLORED_CHARTS, LOADING_EXAMPLE, LOADED_EXAMPLE } from '../actions/types';

const initialState = {
    charts: [],
    loading: false,
    recoloring: false,
}

export default function chartsReducer(state=initialState, action) {
    switch(action.type) {
        case GET_CHARTS:
            return {
                ...state,
                charts: action.payload
            }
        case ADD_CHARTS:
            return {
                ...state,
                charts: action.payload
            }
        case DELETE_CHART:
            return {
                ...state,
                charts: state.charts.filter(chart => chart.id !== action.payload),
            }
        case UPDATE_CHART:
            return {
                ...state,
                charts: action.payload
            }
        case RECOLORING_CHARTS:
            return {
                ...state,
                recoloring: true,
            }
        case RECOLORED_CHARTS:
            return {
                ...state,
                charts: action.payload,
                recoloring: false,
            }
        case LOADING_EXAMPLE:
            return {
                ...state,
                loading: true,
            }
        case LOADED_EXAMPLE:
            return {
                ...state,
                charts: action.payload,
                loading: false,
            }
        default:
            return state
    }
}