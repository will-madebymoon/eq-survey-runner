// >>> WARNING THIS PAGE WAS AUTO-GENERATED - DO NOT EDIT!!! <<<
const QuestionPage = require('../question.page');

class SummaryPage extends QuestionPage {

  constructor() {
    super('summary');
  }

  building() { return '#building-answer'; }

  buildingEdit() { return '[data-qa="building-edit"]'; }

  addressLine1() { return '#address-line-1-answer'; }

  addressLine1Edit() { return '[data-qa="address-line-1-edit"]'; }

  addressLine2() { return '#address-line-2-answer'; }

  addressLine2Edit() { return '[data-qa="address-line-2-edit"]'; }

  addressLine3() { return '#address-line-3-answer'; }

  addressLine3Edit() { return '[data-qa="address-line-3-edit"]'; }

  townCity() { return '#town-city-answer'; }

  townCityEdit() { return '[data-qa="town-city-edit"]'; }

  county() { return '#county-answer'; }

  countyEdit() { return '[data-qa="county-edit"]'; }

  postcode() { return '#postcode-answer'; }

  postcodeEdit() { return '[data-qa="postcode-edit"]'; }

  country() { return '#country-answer'; }

  countryEdit() { return '[data-qa="country-edit"]'; }

  firstText() { return '#first-text-answer'; }

  firstTextEdit() { return '[data-qa="first-text-edit"]'; }

  secondText() { return '#second-text-answer'; }

  secondTextEdit() { return '[data-qa="second-text-edit"]'; }

  multiplePipingAnswer() { return '#multiple-piping-answer-answer'; }

  multiplePipingAnswerEdit() { return '[data-qa="multiple-piping-answer-edit"]'; }

}
module.exports = new SummaryPage();
