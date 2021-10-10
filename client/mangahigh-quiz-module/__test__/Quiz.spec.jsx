import React from 'react';
import { shallow, mount } from 'enzyme';
import Quiz from '../src/Quiz';
import axios from "axios";
import { act } from "react-dom/test-utils";
jest.mock('axios');

jest.mock('mangahigh-libs/react', () => jest.requireActual('react'),
	{ virtual: true }
);

jest.mock('mangahigh-components/Button', () => () => 'Button'			
, { virtual: true });

jest.mock('mangahigh-components/MultiOptions', () => () => 'MultiOptions'			
, { virtual: true });

const response = {
	"data": [{
		"_id":"test_id",
		"questions":[
				{
				"id":"maths_question_1",
				"question":"test_question_1",
				"options":["option_1","option_2"],
				"answer":"974"
			},
			{
				"id":"maths_question_2",
				"question":"test_question_2",
				"options":["option_1","option_2"],
				"answer":"50"
			},			
		],
	}],
};

describe('Test Quiz Component', () => {
	let renderedModule;
	afterEach(() => {
    jest.clearAllMocks();
  });

	it('should show loading state while fetching data from DB', () => {		
		renderedModule = shallow(<Quiz />);
		expect(renderedModule.find('.spinner-border').exists()).toBeTruthy();
	});

	it('should render QuizIntro on succesful data fetch', async () => {
		await act(async () => {
      await axios.get.mockImplementationOnce(() => Promise.resolve(response));  
      renderedModule = mount(<Quiz />);    
    });		
		renderedModule.update();
		await expect(axios.get).toHaveBeenCalledTimes(1);		
		expect(renderedModule.find('QuizIntro').exists()).toBeTruthy();
	});

	// using callback instead of button onClick simulation - see QuizIntro.spec.jsx line#26 
	it('should render Questions when component gets an update to set to quiz', () => {		
		act(() => {
			renderedModule.find('QuizIntro').props().updateProgress('quiz');
		});
		renderedModule.update();		
		expect(renderedModule.find('Question').exists()).toBeTruthy();
		expect(renderedModule.find('h5').text()).toEqual('test_question_1');
	});

	it('should render Next Questions when the current state and next state are same', () => {		
		act(() => {
			renderedModule.find('Question').props().getSelectedValue('option_1');
			renderedModule.find('Question').props().updateProgress('quiz');
		});
		renderedModule.update();
		expect(renderedModule.find('h5').text()).toEqual('test_question_2');
	});

	it('should show submission at the end of quiz', () => {		
		act(() => {
			renderedModule.find('Question').props().updateProgress('result');
		});
		renderedModule.update();		
		expect(renderedModule.find('Result').exists()).toBeTruthy();
	});

	it('should show Questions again on Play Again from result section', async () => {				
		await act(async () => {
			await axios.get.mockImplementationOnce(() => Promise.resolve(response));  
			renderedModule.find('Result').props().updateProgress('playAgain');
		});		
		renderedModule.update();		
		expect(renderedModule.find('Question').exists()).toBeTruthy();
	});
});