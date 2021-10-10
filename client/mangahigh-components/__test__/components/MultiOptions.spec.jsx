import React from 'react';
import { shallow } from 'enzyme';
import MultiOptions from '../../src/components/MultiOptions';

describe('Test MultiOptions Component', () => {  
	it('with required props', () => {
    const multiOptionsValues = ['Option 1', 'Option 2'];
		const renderedModule = shallow(
     <MultiOptions 
      options={multiOptionsValues} 
      groupName='test_multi_option' 
      getSelectedValue={jest.fn()} 
    />);
    expect(renderedModule).toMatchSnapshot();
	});

  it('should return selected value on change', () => {
    const multiOptionsValues = ['Option 1'];
    const mockCallback = jest.fn();
    const eventObj = {
      target: {
        value: 'test',
      },
    };
    const renderedModule = shallow(<MultiOptions 
      options={multiOptionsValues} 
      groupName='test_multi_option' 
      getSelectedValue={mockCallback} 
    />);    
    renderedModule.simulate('change', eventObj);
    expect(mockCallback).toHaveBeenCalledWith(eventObj.target.value);
  });
});