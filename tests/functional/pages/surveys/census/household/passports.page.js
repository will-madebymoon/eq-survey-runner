// >>> WARNING THIS PAGE WAS AUTO-GENERATED - DO NOT EDIT!!! <<<
const QuestionPage = require('../../question.page');

class PassportsPage extends QuestionPage {

  constructor() {
    super('passports');
  }

  unitedKingdom() {
    return '#passports-answer-0';
  }

  irish() {
    return '#passports-answer-1';
  }

  other() {
    return '#passports-answer-2';
  }

  none() {
    return '#passports-answer-3';
  }

}
module.exports = new PassportsPage();
