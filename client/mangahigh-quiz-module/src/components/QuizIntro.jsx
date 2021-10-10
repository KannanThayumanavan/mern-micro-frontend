import React from 'mangahigh-libs/react';
import Button from 'mangahigh-components/Button';
import PropTypes from 'prop-types';

const QuizIntro = ({ introHeader, updateProgress }) => (
	<div className="p-3">
		<h5 className="p-3">{introHeader}</h5>		
		<Button
	  	type='success'
	  	buttonLabel='Start Quiz'
	  	buttonOnClick={() => updateProgress('quiz')}
		/>
	</div>
);

QuizIntro.propTypes = {
	introHeader: PropTypes.string.isRequired,
	updateProgress: PropTypes.func.isRequired,
};

export default QuizIntro;