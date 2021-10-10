import React from 'react';
import { shallow, mount } from 'enzyme';
import Button from '../../src/components/Button';

describe('Test Button Component', () => {
	it('should render correctly with required props', () => {
		const renderedModule = shallow(<Button
      type='primary'
      buttonLabel='Test Button'
      buttonOnClick={jest.fn()}
    />);
    expect(renderedModule).toMatchSnapshot();
	});
});