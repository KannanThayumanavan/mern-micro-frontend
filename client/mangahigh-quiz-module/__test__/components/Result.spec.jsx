import React from 'react';
import { shallow } from 'enzyme';
import Result from '../../src/components/Result';

jest.mock('mangahigh-libs/react', () => jest.requireActual('react'),
	{ virtual: true }
);

jest.mock('mangahigh-components/Button', () => 'Button'			
, { virtual: true });

describe('Test Result Component', () => {
	const mockCallback = jest.fn();
	const props = {
		questions: [
			{
				id: 'test_id',
				question: 'test question 1',
				options: ['test option 1', 'test option 2'],
				userAnswer: 'test option 1',
				answer: 'test option 2',
			}
		],
		updateProgress: mockCallback,
	};
	
	it('should render correctly with required props', () => {
		const renderedModule = shallow(<Result {...props} />);
    expect(renderedModule).toMatchSnapshot();
	});

	it('should callback when Button clicked', () => {
		const renderedModule = shallow(<Result {...props} />);		
    renderedModule.find('Button').props().buttonOnClick(); // see QuizIntro.spec.jsx line#26 
		expect(mockCallback).toHaveBeenCalledWith('playAgain');
	});
});