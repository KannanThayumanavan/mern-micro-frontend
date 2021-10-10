import React from 'react';
import Button from './src/components/Button';
import DisplayCard from './src/components/DisplayCard';
import Table from './src/components/Table';
import MultiOptions from './src/components/MultiOptions';
import './src/styles/bootstrap.min.css';

const tableData = {
  header: ['Heading 1', 'Heading 2'],
  rows: [
    ['Row1 Data1', 'Row1 data2'],
    ['Row2 Data1', 'Row2 data2'],
  ],
};
const multiOptionsValues = ['Option 1', 'Option 2', 'Option 3'];
const getSelectedValue = (value) => console.log(value);
const buttonOnClick = () => console.log('Button click');

// Purely for demo purpose and no unit test required.
const App = () => (
  <div className="container-fluid">
    <h4>Re-usable Components</h4><hr />
    
    <h5>Button</h5>
    <Button
      type='primary'
      buttonLabel='Test Button'
      buttonOnClick={buttonOnClick}
    /><hr />

    <h5>DisplayCard</h5>
    <DisplayCard
      highlight='16'
      summary='times attempted'
    /><hr />

    <h5>MultiOptions</h5>
    <MultiOptions 
      options={multiOptionsValues} 
      groupName='test_multi_option' 
      getSelectedValue={getSelectedValue} 
    /><hr />

    <h5>Table</h5>
    <Table tableData={tableData} /><hr />
  </div>
);

export default App;