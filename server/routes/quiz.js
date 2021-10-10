const express = require("express");

// quizRoutes is an instance of the express router.
// We use it to define our routes.
// The router will be added as a middleware and will take control of requests starting with path /quiz and /attempts.
const quizRoutes = express.Router();

const dbo = require("../db/conn");

// This help convert the id from string to ObjectId for the _id.
const ObjectId = require("mongodb").ObjectId;


quizRoutes.route("/quiz").get(function (req, res) {
  let db_connect = dbo.getDb();
  db_connect
    .collection("quiz")
    .find({})
    .toArray(function (err, result) {
      if (err) throw err;
      res.json(result);
    });
});

quizRoutes.route("/attempts").get(function (req, res) {
  let db_connect = dbo.getDb();
  db_connect
    .collection("attempts")
    .find({})
    .toArray(function (err, result) {
      if (err) throw err;
      res.json(result);
    });
});

quizRoutes.route("/attempts/add").post(function (req, response) {
  let db_connect = dbo.getDb();
  let newAttempt = {
    date_and_time: req.body.date_and_time,
    score: req.body.score,
    total_questions: req.body.total_questions,
  };
  db_connect.collection("attempts").insertOne(newAttempt, function (err, res) {
    if (err) throw err;
    response.json(res);
  });
});

module.exports = quizRoutes;