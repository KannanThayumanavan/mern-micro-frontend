import React, { useState, useEffect } from 'mangahigh-libs/react';
import QuizIntro from './components/QuizIntro';
import Question from './components/Question';
import Result from './components/Result';
import { 
	logResult, fetchQuestions, changeQuestion, isLastQuestion,
} from './utils/utils';

const Quiz = () => {
	const [questions, setQuestions] = useState([]);	
	const [currentQuestion, setCurrentQuestion] = useState(0);	
	const [currentState, setCurrentState] = useState('start');
	
	useEffect(() => {		
		fetchQuestions()
			.then((fetchedQuestions) => setQuestions(fetchedQuestions));	
	}, []);

	const updateProgress = (updatedState) => {
		if(updatedState === currentState) {
			changeQuestion(currentQuestion, setCurrentQuestion);
		} else {
			if (updatedState === 'result') {
				logResult(questions);				
			}
			if (updatedState === 'playAgain') {
				setCurrentState('quiz');
				fetchQuestions()
					.then((fetchedQuestions) => setQuestions(fetchedQuestions));				
				setCurrentQuestion(0);
			} else {
				setCurrentState(updatedState);	
			}
		}		
	}

	const getSelectedValue = (selectedValue) => {		
		const getCurrentQuestions = [...questions];
		getCurrentQuestions[currentQuestion] = ({
			... getCurrentQuestions[currentQuestion], 
			userAnswer: selectedValue
		});
		setQuestions(getCurrentQuestions);		
	};

	return(
		<div className="container-fluid p-3">
	  	<div className="row text-center">
	    	<div className="col-md-12">
	    	{questions.length === 0 && (
	    		<div className="spinner-border text-primary" role="status">
					  <span className="visually-hidden">Loading...</span>
					</div>	
	    	)}
	    	{questions && questions.length > 1 && (
	    		<div className="p-3 border bg-light">		     		
						{(currentState === 'start') && (
							<QuizIntro 
								introHeader='Maths Quiz. 3 Questions.' 
								updateProgress={updateProgress} 
							/>								
						)}						
						{(currentState === 'quiz' || currentState === 'playAgain') && (
							<div>
								<div className="text-left"><h4>Question {currentQuestion + 1}<small>/{questions.length}</small></h4></div>
				     		<Question 
			     		 		question={questions[currentQuestion]} 
			     		 		getSelectedValue={getSelectedValue}
			     		 		showSubmission={isLastQuestion(questions, currentQuestion)}
			     		 		updateProgress={updateProgress}
			     		 	/>
		     		 	</div>
	     			)}
	     			{(currentState === 'result') && (
	     				<Result 
	     					questions={questions} 
	     					updateProgress={updateProgress} 
	     				/>
	     			)}
		     	</div>
    		)}
		    </div>		        	
		  </div>	
		</div>		
	);
};

export default Quiz;