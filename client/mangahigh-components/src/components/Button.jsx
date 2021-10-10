import React from 'react';
import PropTypes from 'prop-types';

const Button = ({ type, buttonOnClick, buttonLabel }) => (
	<button 
		type="button" 
		className={`btn btn-${type}`}
		onClick={buttonOnClick}
		value={buttonLabel}
	>
		{buttonLabel}
	</button>
);

Button.propTypes = {
	type: PropTypes.string.isRequired, 
	buttonOnClick: PropTypes.func.isRequired,
	buttonLabel: PropTypes.string.isRequired,
};

export default Button;