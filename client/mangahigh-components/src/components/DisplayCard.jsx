import React from 'react';
import PropTypes from 'prop-types';

const DisplayCard = ({ highlight, summary }) => (	
	<div className="card border-success mb-3">
	  <div className="card-header">{summary}</div>
	  <div className="card-body text-success">
	    <h5 className="card-title h1">{highlight}</h5>		    
	  </div>
	</div>
);

DisplayCard.propTypes = {
	highlight: PropTypes.string.isRequired, 
	summary: PropTypes.string.isRequired,
};
export default DisplayCard;