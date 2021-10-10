import React from 'react';
import { shallow, mount } from 'enzyme';
import Insights from '../src/Insights';
import axios from "axios";
import { act } from "react-dom/test-utils";

jest.mock('axios');

jest.mock('mangahigh-libs/react', () => jest.requireActual('react'),
	{ virtual: true }
);

jest.mock('mangahigh-components/DisplayCard', () => () => 'DisplayCard'			
, { virtual: true });

jest.mock('mangahigh-components/Table', () => () => 'Table'			
, { virtual: true });

const response = {
	data: [
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
	],
}

describe('Test Insights Component', () => {
	let renderedModule;
	afterEach(() => {
    jest.clearAllMocks();
  });

	it('should render loading state correctly', () => {
		renderedModule = shallow(<Insights />);
		expect(renderedModule.find('.spinner-border').exists()).toBeTruthy();
    expect(renderedModule).toMatchSnapshot();
	});

	it('should render Insights component with succesfull fetch call', async () => {
		await act(async () => {
      await axios.get.mockImplementationOnce(() => Promise.resolve(response));  
      renderedModule = mount(<Insights />);    
    });		
		renderedModule.update();
		await expect(axios.get).toHaveBeenCalledTimes(1);
		expect(renderedModule.find('Summary').exists()).toBeTruthy();
		expect(renderedModule.find('AttemptsDataTable').exists()).toBeTruthy();		
		expect(renderedModule).toMatchSnapshot();
	});
});