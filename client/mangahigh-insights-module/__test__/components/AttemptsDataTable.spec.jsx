import React from 'react';
import { shallow, mount } from 'enzyme';
import AttemptsDataTable from '../../src/components/AttemptsDataTable';

jest.mock('mangahigh-libs/react', () => jest.requireActual('react'),
	{ virtual: true }
);

jest.mock('mangahigh-components/Table', () => () => 'Table'			
, { virtual: true });

describe('Test AttemptsDataTable Component', () => {
	const attempts = [
		{
			"_id":"6161b01c74f86b0917b418c8",
			"date_and_time":"2021-10-09T15:07:07.763Z",
			"score":3,
			"total_questions":3
		},
		{
			"_id":"6161b01c74f86b0917b418b6",
			"date_and_time":"2021-10-09T15:37:07.763Z",
			"score":1,
			"total_questions":3
		}
	];
	it('should render correctly with required props', () => {
		const renderedModule = shallow(<AttemptsDataTable attempts={attempts} />);
    expect(renderedModule).toMatchSnapshot();
	});
});