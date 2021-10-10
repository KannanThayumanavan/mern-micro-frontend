import React from 'react';
import {shallow } from 'enzyme';
import Summary from '../../src/components/Summary';

jest.mock('mangahigh-libs/react', () => jest.requireActual('react'),
	{ virtual: true }
);

jest.mock('mangahigh-components/DisplayCard', () => () => 'DisplayCard'			
, { virtual: true });

describe('Test Summary Component', () => {
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
		const renderedModule = shallow(<Summary attempts={attempts} />);
    expect(renderedModule).toMatchSnapshot();
	});
});