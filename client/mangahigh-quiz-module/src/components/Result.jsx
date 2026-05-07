import React, { Fragment, useEffect, useState } from 'react';
import Button from '../../../../mangahigh-components/src/components/Button';
import { calculateResult } from '../utils/utils';
import PropTypes from 'prop-types';

const Result = ({
	questions, updateProgress,
}) => (
	<div className="p-3">
		<h5 className="p-3">You scored {calculateResult(questions)} out of {questions.length}</h5>
		{updateProgress && (
			<Button
			  type='success'
			  buttonLabel='Play again'
			  buttonOnClick={() => updateProgress('playAgain')}
			/>
		)}
	</div>		
);

Result.propTypes = {
	questions: PropTypes.arrayOf(PropTypes.shape({
		id: PropTypes.string.isRequired,
		question: PropTypes.string.isRequired,
		options: PropTypes.arrayOf(PropTypes.string).isRequired,
		userAnswer: PropTypes.string,
		answer: PropTypes.string.isRequired,
	})),
	updateProgress: PropTypes.func.isRequired,
};
export default Result;




