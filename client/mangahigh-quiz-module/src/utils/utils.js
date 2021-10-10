import axios from 'axios';

export const calculateResult = (questions) => questions
	.map((question) => question.answer === question.userAnswer)
	.filter(Boolean).length;

export const changeQuestion = (
	currentQuestion, setCurrentQuestion
) => setCurrentQuestion(currentQuestion + 1);	
	
export const isLastQuestion = (
	questions, currentQuestion
) => questions.length === currentQuestion + 1;

export const logResult = (questions) => {
	const newAttempt = {
		date_and_time: new Date(),
		score: calculateResult(questions),	
		total_questions: questions.length,
	};
	axios
    .post("http://localhost:5000/attempts/add", newAttempt);
};

export const fetchQuestions = () => axios
		.get("http://localhost:5000/quiz")
		.then((res) => res.data[0].questions);

