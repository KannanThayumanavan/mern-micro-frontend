import React from "mangahigh-libs/react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
} from "mangahigh-libs/react-router-dom";
import InsightsComponent from "mangahigh-insights-module/App";
import QuizComponent from "mangahigh-quiz-module/App";

const Insights = () => <InsightsComponent />;
const Quiz = () => <QuizComponent />;

const App = () => (
  <Router> 
    <nav className="navbar sticky-top navbar-dark bg-success">        
      <ul className="nav">
        <li className="nav-item">
          <div className="nav-link active">
            <Link to="/"><span className="text-white">Insights</span></Link>
          </div>
        </li>
        <li>
          <div className="nav-link active">
            <Link to="/quiz"><span className="text-white">Quiz</span></Link>
          </div>
        </li>            
      </ul> 
      <Link to="/">
        <span className="text-white navbar-brand">Mangahigh Tech assignment</span>
      </Link>
    </nav>         
    <div className="container-fluid">              
      <div className="row p-3">
        <Switch>
          <Route path="/quiz">
            <Quiz />
          </Route>      
          <Route path="/">
            <Insights />
          </Route>
        </Switch>
      </div>
    </div>
  </Router>
);

export default App;

