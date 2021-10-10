import React from 'mangahigh-libs/react';
import Table from 'mangahigh-components/Table';
import PropTypes from 'prop-types';

const populateRowsToDisplay = (attempts) => attempts.map((attempt, index) => [
	(index + 1).toString(),
	new Date(attempt.date_and_time).toUTCString(),
	attempt.score.toString(),
	attempt.total_questions.toString(),
]);

const AttemptsDataTable = ({ attempts }) => {	
	const tableData = {
	  header: ['#', 'Date and time of play', 'Score', 'Total Questions'],
	  rows: [...populateRowsToDisplay(attempts)],
	};
	return (
		<div className="row">
			<div className="col-md-12">
				<h4 className="text-left">Historical Results <small>(latest on top)</small></h4>
				<Table tableData={tableData} />
			</div>
		</div>
	);
}

AttemptsDataTable.propTypes = {
	attempts: PropTypes.arrayOf(PropTypes.shape({
		date_and_time: PropTypes.string,
		score: PropTypes.number,
		total_questions: PropTypes.number,
	})).isRequired
};

export default AttemptsDataTable;