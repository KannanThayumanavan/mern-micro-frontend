import React from 'react';
import PropTypes from 'prop-types';

const MultiOptions = ({ 
  options, groupName, getSelectedValue,
}) => options.map((option) => (
  <div 
    key={`${groupName}_${option}`} 
    className="form-check form-check-inline p-3" 
    onChange={(e) => getSelectedValue(e.target.value)}
  >
    <input className="form-check-input" type="radio" name={groupName} value={option} id={option} />
    <label className="form-check-label" htmlFor={option}>{option}</label>
  </div>
));

MultiOptions.propTypes = {
  options: PropTypes.arrayOf(PropTypes.string).isRequired,
  groupName: PropTypes.string.isRequired,
  getSelectedValue: PropTypes.func.isRequired,
};
      
export default MultiOptions;