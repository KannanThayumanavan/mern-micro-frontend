import React from 'mangahigh-libs/react';
import DisplayCard from 'mangahigh-components/DisplayCard';
import PropTypes from 'prop-types';

const calculateAverage = (attempts) => attempts
	.map((attempt) => attempt.score)
	.reduce((accumulator, currentValue) => accumulator + currentValue) / attempts.length;

const Summary = ({ attempts }) =>  (	
	<div className="row">			
		<div className="col-md-6">
			<DisplayCard
		    highlight={(attempts.length).toString()}
		    summary='Number of times played'
		  />
	  </div>	
	  <div className="col-md-6">
		  <DisplayCard
		    highlight={(calculateAverage(attempts).toFixed(1)).toString()}
		    summary='Average score'
		  />
		</div>		
  </div>
);

Summary.propTypes = {
	attempts: PropTypes.arrayOf(PropTypes.shape({
		date_and_time: PropTypes.string,
		score: PropTypes.number,
		total_questions: PropTypes.number,
	})).isRequired
};

export default Summary;