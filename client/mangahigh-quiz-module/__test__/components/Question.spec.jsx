import React from 'react';
import { shallow } from 'enzyme';
import Question from '../../src/components/Question';

jest.mock('mangahigh-libs/react', () => jest.requireActual('react'),
	{ virtual: true }
);

jest.mock('mangahigh-components/Button', () => 'Button'			
, { virtual: true });

jest.mock('mangahigh-components/MultiOptions', () => 'MultiOptions'			
, { virtual: true });

describe('Test Question Component', () => {
	const mockCallback = jest.fn();
	const props = {
		question: {
			id: 'test_id',
			question: 'test question 1',
			options: ['test option 1', 'test option 2'],
		},
		getSelectedValue: jest.fn(),
		showSubmission: false, 
		updateProgress: mockCallback,
	};
	
	describe('Test navigation between quiz questions', () => {
		it('should render correctly with required props', () => {
			const renderedModule = shallow(<Question {...props} />);
	    expect(renderedModule).toMatchSnapshot();
		});

		it('should callback to change question on click of Next button', () => {
			const renderedModule = shallow(<Question {...props} />);
			renderedModule.find('Button').props().buttonOnClick();
			expect(mockCallback).toHaveBeenCalledWith('quiz');
		});
	});
	
	describe('Test quiz submission and result section', () => {
		const endQuizProp = {
			...props,
			showSubmission: true, 
		};
		it('should show Submit button at end of Quiz', () => {			
			const renderedModule = shallow(<Question {...endQuizProp} />);		
	    expect(renderedModule).toMatchSnapshot();
		});

		it('should callback to play again on click of Play again button', () => {
			const renderedModule = shallow(<Question {...endQuizProp} />);
			renderedModule.find('Button').props().buttonOnClick();
			expect(mockCallback).toHaveBeenCalledWith('result');
		});
	});
});