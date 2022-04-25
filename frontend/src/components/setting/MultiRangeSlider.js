import React, { useCallback, useEffect, useState, useRef } from "react";
import PropTypes from "prop-types";


const MultiRangeSlider = ({ min, max, rangeMin, rangeMax, onMouseUp, mouseup }) => {
  const [minVal, setMinVal] = useState(min);
  const [maxVal, setMaxVal] = useState(max);
  const [mouseupVal, setMouseupVal] = useState(mouseup)
  const minValRef = useRef(min);
  const maxValRef = useRef(max);
  const mouseupValRef = useRef(mouseup);
  const range = useRef(null);

  // Convert to percentage
  const getPercent = useCallback(
    (value) => Math.round(((value - rangeMin) / (rangeMax - rangeMin)) * 100),
    [min, max, rangeMin, rangeMax]
  );

  // Set width of the range to decrease from the left side
  useEffect(() => {
    const minPercent = getPercent(minVal);
    const maxPercent = getPercent(maxValRef.current);
    const realminPercent = Math.min(minPercent, maxPercent);
    const realmaxPercent = Math.max(minPercent, maxPercent);

    if (range.current) {
      range.current.style.left = `${realminPercent}%`;
      range.current.style.width = `${realmaxPercent - realminPercent}%`;
    }
  }, [minVal, getPercent]);

  // Set width of the range to decrease from the right side
  useEffect(() => {
    const minPercent = getPercent(minValRef.current);
    const maxPercent = getPercent(maxVal);
    const realminPercent = Math.min(minPercent, maxPercent);
    const realmaxPercent = Math.max(minPercent, maxPercent);

    if (range.current) {
      range.current.style.left = `${realminPercent}%`;
      range.current.style.width = `${realmaxPercent - realminPercent}%`;
    }
  }, [maxVal, getPercent]);

// Get min and max values when their state changes
  useEffect(() => {
    onMouseUp({ min: minVal, max: maxVal });
  }, [mouseupVal]);

  return (
    <div className="multirangeslider-parent">
      <input
        type="range"
        min={rangeMin}
        max={rangeMax}
        value={minVal}
        onChange={(event) => {
          const value = Number(event.target.value);
          setMinVal(value);
          minValRef.current = value;
        }}
        onMouseUp={(event) => {
          const value = !mouseupVal;
          setMouseupVal(value);
          mouseupValRef.current = value;
        }}
        className="thumb thumb--left"
        style={{ zIndex: (minVal > 5 && max !== 1) && "5" }}
      />
      <input
        type="range"
        min={rangeMin}
        max={rangeMax}
        value={maxVal}
        step="1"
        onChange={(event) => {
          const value = Number(event.target.value);
          setMaxVal(value);
          maxValRef.current = value;
        }}
        onMouseUp={(event) => {
          const value = !mouseupVal;
          setMouseupVal(value);
          mouseupValRef.current = value;
        }}
        className="thumb thumb--right"
      />

      <div className="multirange-slider">
        <div className="slider__track" />
        <div ref={range} className="slider__range" />
        <div className="slider__left-value">{Math.min(minVal, maxVal)}</div>
        <div className="slider__right-value">{Math.max(minVal, maxVal)}</div>
      </div>
    </div>
  );
};

MultiRangeSlider.propTypes = {
  min: PropTypes.number.isRequired,
  max: PropTypes.number.isRequired,
  rangeMin: PropTypes.number.isRequired,
  rangeMax: PropTypes.number.isRequired,
  mouseup: PropTypes.bool.isRequired,
  onMouseUp:PropTypes.func.isRequired
};

export default MultiRangeSlider;