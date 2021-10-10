import React from 'mangahigh-libs/react';
import Button from 'mangahigh-components/Button';
import MultiOptions from 'mangahigh-components/MultiOptions';
import PropTypes from 'prop-types';

const Question = ({ 
	question: {
		id,
		question,
		options,
	},
	getSelectedValue,
	showSubmission, 
	updateProgress,
}) => (
	<div className="p-3">
		<h5>{question}</h5>
		<MultiOptions 
	    options={options} 
	    groupName={id}
	    getSelectedValue={getSelectedValue} 
  	/>
  	<div className="p-3">
  	{showSubmission
  		? (
  				<Button 
						type='primary' 
						buttonLabel='Submit' 
						buttonOnClick={() => updateProgress('result')}
					/>
  			)
  		: (
  				<Button 
						type='primary' 
						buttonLabel='Next'
						buttonOnClick={() => updateProgress('quiz')}
					/>					
  			)
  	}
  	</div>
		
	</div>
);

Question.propTypes = {
	question: PropTypes.shape({
		id: PropTypes.string.isRequired,
		question: PropTypes.string.isRequired,
		options: PropTypes.arrayOf(PropTypes.string).isRequired,
	}),
	getSelectedValue: PropTypes.func.isRequired,
	showSubmission: PropTypes.bool.isRequired,
	updateProgress: PropTypes.func.isRequired,
};

export default Question;