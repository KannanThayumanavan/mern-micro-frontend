import React from 'react';
import { shallow } from 'enzyme';
import Table from '../../src/components/Table';

describe('Test Table Component', () => {
  const tableData = {
    header: ['Heading 1', 'Heading 2'],
    rows: [
      ['Row1 Data1', 'Row1 data2'],
      ['Row2 Data1', 'Row2 data2'],
    ],
  };
	it('should render correctly with required props', () => {
		const renderedModule = shallow(<Table tableData={tableData} />);
    expect(renderedModule).toMatchSnapshot();
	});
});