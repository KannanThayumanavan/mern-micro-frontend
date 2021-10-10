import React, { useEffect, useState } from 'mangahigh-libs/react';
import Summary from './components/Summary';
import AttemptsDataTable from './components/AttemptsDataTable';
import axios from 'axios';

const Insights = ({}) => {
  const [attempts, setAttempts] = useState(null);

  useEffect(() => {
    axios
      .get("http://localhost:5000/attempts")
      .then((res) => {
        const sortResponseBasedOnDate = res.data
          .sort((obj1, obj2) => new Date(obj2.date_and_time) - new Date(obj1.date_and_time));          
        setAttempts(sortResponseBasedOnDate);
      })
  }, []);

  return(
    <div className="container-fluid p-3">
      <div className="row text-center">
        <div className="col-md-12">
        {!attempts && (
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>  
        )}
        {attempts && (
          <div className="p-3 border bg-light">
            <Summary attempts={attempts} />
            <AttemptsDataTable attempts={attempts} />
          </div>
        )}
        </div>
      </div>
    </div>  
  );
};

export default Insights;