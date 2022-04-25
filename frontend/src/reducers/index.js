import { combineReducers } from 'redux';
import colorschemesReducer from './colorschemes';
import colorsReducer from './colors';
import colorconfigReducer from './colorconfig';
import datasetsReducer from './datasets';
import chartsReducer from './charts';
import paramReducer from './parameters';
import examplesReducer from './examples';
import colorencodingsReducer from './colorencodings';
import rangecolorsReducer from './rangecolors';
import mvcolorencodingsReducer from './mvcolorencodings';
import mvconceptgroupingsReducer from './mvconceptgroupings';

export default combineReducers({
    colorschemesReducer,
    colorsReducer,
    colorconfigReducer,
    datasetsReducer,
    chartsReducer,
    paramReducer,
    examplesReducer,
    colorencodingsReducer,
    rangecolorsReducer,
    mvcolorencodingsReducer,
    mvconceptgroupingsReducer,
});