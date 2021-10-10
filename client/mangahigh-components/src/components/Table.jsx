import React from 'react';
import PropTypes from 'prop-types';

const Table = ({ tableData }) => (
	<table className="table table-striped table-hover table-light">
	  <thead>
	    <tr>
	    	{tableData.header.map((header) => <th key={header} scope="col">{header}</th>)}		      
	    </tr>
	  </thead>
	  <tbody>
	  	{tableData.rows.map((row) => (
	  		<tr key={row}>
	  			{row.map((data, index) => <td key={`${data}_${index}`}>{data}</td>)}
	  		</tr>
	  	))}
	  </tbody>
	</table>
);

Table.propTypes = {
	tableData: PropTypes.shape({
		header: PropTypes.arrayOf(PropTypes.string).isRequired,
		rows: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.string)).isRequired,
	}),
};

export default Table;
