import React from 'react';
import { shallow } from 'enzyme';
import DisplayCard from '../../src/components/DisplayCard';

describe('Test DisplayCard Component', () => {
	it('with required props', () => {
		const renderedModule = shallow(
      <DisplayCard
      highlight='16'
      summary='times attempted'
    />);
    expect(renderedModule).toMatchSnapshot();
	});
});