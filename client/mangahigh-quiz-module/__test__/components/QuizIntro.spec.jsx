import React from 'react';
import { shallow, mount } from 'enzyme';
import QuizIntro from '../../src/components/QuizIntro';

jest.mock('mangahigh-libs/react', () => jest.requireActual('react'),
	{ virtual: true }
);

jest.mock('mangahigh-components/Button', () => 'Button',	
{ virtual: true });

describe('Test QuizIntro Component', () => {
	const mockCallback = jest.fn();
	const props = {
		introHeader: 'test header', 
		updateProgress: mockCallback,
	};
	
	it('should render correctly with required props', () => {
		const renderedModule = shallow(<QuizIntro {...props} />);
    expect(renderedModule).toMatchSnapshot();
	});

	it('should callback when Button clicked', () => {
		const renderedModule = shallow(<QuizIntro {...props} />);								
		// renderedModule.find('Button').simulate('click'); --> line#26 - usual way
		/* line#28 - because remote module(mangahigh-components) actual components are not available 
		*	 https://scriptedalchemy.medium.com/module-federation-how-do-we-create-unit-tests-for-it-bd0d73c999bc	 
		*/
		renderedModule.find('Button').props().buttonOnClick(); 
		expect(mockCallback).toHaveBeenCalledWith('quiz');		
	});
});