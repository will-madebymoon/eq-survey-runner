const helpers = require('../../helpers');

const FirstNumberBlockPage = require('../../pages/features/calculated_summary/first-number-block.page.js');
const SecondNumberBlockPage = require('../../pages/features/calculated_summary/second-number-block.page.js');
const ThirdNumberBlockPage = require('../../pages/features/calculated_summary/third-number-block.page.js');
const FourthNumberBlockPage = require('../../pages/features/calculated_summary/fourth-number-block.page.js');
const FifthNumberBlockPage = require('../../pages/features/calculated_summary/fifth-number-block.page.js');
const SixthNumberBlockPage = require('../../pages/features/calculated_summary/sixth-number-block.page.js');
const CurrencyTotalPlaybackPage = require('../../pages/features/calculated_summary/currency-total-playback.page.js');
const UnitTotalPlaybackPage = require('../../pages/features/calculated_summary/unit-total-playback.page.js');
const PercentageTotalPlaybackPage = require('../../pages/features/calculated_summary/percentage-total-playback.page.js');
const NumberTotalPlaybackPage = require('../../pages/features/calculated_summary/number-total-playback.page.js');
const SummaryPage = require('../../pages/summary.page.js');
const ThankYouPage = require('../../pages/thank-you.page.js');

describe('Feature: Calculated Summary', function() {

  describe('Given I have a Calculated Summary', function() {

    before('Get to Calculated Summary', function () {
      return helpers.openQuestionnaire('test_calculated_summary.json').then(() => {
        return browser
          .setValue(FirstNumberBlockPage.answer(), 1.23)
        .click(FirstNumberBlockPage.submit())

        .setValue(SecondNumberBlockPage.secondNumber(), 4.56)
        .setValue(SecondNumberBlockPage.secondNumberUnitTotal(), 789)
        .setValue(SecondNumberBlockPage.secondNumberAlsoInTotal(), 0.12)
        .click(SecondNumberBlockPage.submit())

        .setValue(ThirdNumberBlockPage.thirdNumber(), 3.45)
        .setValue(ThirdNumberBlockPage.thirdNumberUnitTotal(), 678)
        .click(ThirdNumberBlockPage.submit())

        .setValue(FourthNumberBlockPage.fourthNumber(), 9.01)
        .setValue(FourthNumberBlockPage.fourthNumberAlsoInTotal(), 2.34)
        .click(FourthNumberBlockPage.submit())

        .setValue(FifthNumberBlockPage.fifthPercent(), 56)
        .setValue(FifthNumberBlockPage.fifthNumber(), 78.91)
        .click(FifthNumberBlockPage.submit())

        .setValue(SixthNumberBlockPage.sixthPercent(), 23)
        .setValue(SixthNumberBlockPage.sixthNumber(), 45.67)
        .click(SixthNumberBlockPage.submit())

        .getUrl().should.eventually.contain(CurrencyTotalPlaybackPage.pageName);
      });
    });

  it('Given I complete every question, When i get to the currency summary, Then I should see the correct total', function() {
    return browser
      // Totals and titles should be shown
      .getText(CurrencyTotalPlaybackPage.calculatedSummaryTitle()).should.eventually.contain('We calculate the total of currency values entered to be £20.71. Is this correct?')
      .getText(CurrencyTotalPlaybackPage.calculatedSummaryQuestion()).should.eventually.contain('Grand total of previous values')
      .getText(CurrencyTotalPlaybackPage.calculatedSummaryAnswer()).should.eventually.contain('£20.71')

      // Answers included in calculation should be shown
      .getText(CurrencyTotalPlaybackPage.firstNumberAnswer()).should.eventually.contain('£1.23')
      .getText(CurrencyTotalPlaybackPage.secondNumberAnswer()).should.eventually.contain('£4.56')
      .getText(CurrencyTotalPlaybackPage.secondNumberAnswerAlsoInTotal()).should.eventually.contain('£0.12')
      .getText(CurrencyTotalPlaybackPage.thirdNumberAnswer()).should.eventually.contain('£3.45')
      .getText(CurrencyTotalPlaybackPage.fourthNumberAnswer()).should.eventually.contain('£9.01')
      .getText(CurrencyTotalPlaybackPage.fourthNumberAnswerAlsoInTotal()).should.eventually.contain('£2.34')

      // Answers not included in calculation should not be shown
      .elements(CurrencyTotalPlaybackPage.secondNumberAnswerUnitTotal()).then(result => result.value).should.eventually.be.empty
      .elements(CurrencyTotalPlaybackPage.thirdNumberAnswerUnitTotal()).then(result => result.value).should.eventually.be.empty
      .elements(CurrencyTotalPlaybackPage.fifthNumberAnswer()).then(result => result.value).should.eventually.be.empty
      .elements(CurrencyTotalPlaybackPage.sixthNumberAnswer()).then(result => result.value).should.eventually.be.empty;
    });

    it('Given change an answer, When i get to the currency summary, Then I should see the new total', function() {
      return browser
        .click(CurrencyTotalPlaybackPage.fourthNumberAnswerEdit())
        .setValue(FourthNumberBlockPage.fourthNumber(), 19.01)
        .setValue(FourthNumberBlockPage.fourthNumberAlsoInTotal(), 12.34)
        .click(FourthNumberBlockPage.submit())

        .click(FifthNumberBlockPage.submit())
        .click(SixthNumberBlockPage.submit())

        .getUrl().should.eventually.contain(CurrencyTotalPlaybackPage.pageName)
        .getText(CurrencyTotalPlaybackPage.calculatedSummaryTitle()).should.eventually.contain('We calculate the total of currency values entered to be £40.71. Is this correct?')
        .getText(CurrencyTotalPlaybackPage.calculatedSummaryAnswer()).should.eventually.contain('£40.71');
    });

    it('Given I leave an answer empty, When i get to the currency summary, Then I should see no answer provided and new total', function() {
      return browser
        .click(CurrencyTotalPlaybackPage.fourthNumberAnswerEdit())
        .setValue(FourthNumberBlockPage.fourthNumber(), '')
        .setValue(FourthNumberBlockPage.fourthNumberAlsoInTotal(), '')
        .click(FourthNumberBlockPage.submit())

        .click(FifthNumberBlockPage.submit())
        .click(SixthNumberBlockPage.submit())

        .getUrl().should.eventually.contain(CurrencyTotalPlaybackPage.pageName)
        .getText(CurrencyTotalPlaybackPage.calculatedSummaryTitle()).should.eventually.contain('We calculate the total of currency values entered to be £9.36. Is this correct?')
        .getText(CurrencyTotalPlaybackPage.calculatedSummaryAnswer()).should.eventually.contain('£9.36')
        .getText(CurrencyTotalPlaybackPage.fourthNumberAnswer()).should.eventually.contain('No answer provided');
    });

    it('Given I complete every question, When i get to the unit summary, Then I should see the correct total', function() {
      return browser
        // Totals and titles should be shown
        .click(CurrencyTotalPlaybackPage.submit())
        .getText(UnitTotalPlaybackPage.calculatedSummaryTitle()).should.eventually.contain('We calculate the total of unit values entered to be 1,467 cm. Is this correct?')
        .getText(UnitTotalPlaybackPage.calculatedSummaryQuestion()).should.eventually.contain('Grand total of previous values')
        .getText(UnitTotalPlaybackPage.calculatedSummaryAnswer()).should.eventually.contain('1,467 cm')

        // Answers included in calculation should be shown
        .getText(UnitTotalPlaybackPage.secondNumberAnswerUnitTotal()).should.eventually.contain('789 cm')
        .getText(UnitTotalPlaybackPage.thirdNumberAnswerUnitTotal()).should.eventually.contain('678 cm');
    });

    it('Given I complete every question, When i get to the percentage summary, Then I should see the correct total', function() {
      return browser
        // Totals and titles should be shown
        .click(UnitTotalPlaybackPage.submit())
        .getText(UnitTotalPlaybackPage.calculatedSummaryTitle()).should.eventually.contain('We calculate the total of percentage values entered to be 79%. Is this correct?')
        .getText(UnitTotalPlaybackPage.calculatedSummaryQuestion()).should.eventually.contain('Grand total of previous values')
        .getText(UnitTotalPlaybackPage.calculatedSummaryAnswer()).should.eventually.contain('79%')

        // Answers included in calculation should be shown
        .getText(PercentageTotalPlaybackPage.fifthPercentAnswer()).should.eventually.contain('56%')
        .getText(PercentageTotalPlaybackPage.sixthPercentAnswer()).should.eventually.contain('23%');
    });

    it('Given I complete every question, When i get to the number summary, Then I should see the correct total', function() {
      return browser
        // Totals and titles should be shown
        .click(UnitTotalPlaybackPage.submit())
        .getText(UnitTotalPlaybackPage.calculatedSummaryTitle()).should.eventually.contain('We calculate the total of number values entered to be 124.58. Is this correct?')
        .getText(UnitTotalPlaybackPage.calculatedSummaryQuestion()).should.eventually.contain('Grand total of previous values')
        .getText(UnitTotalPlaybackPage.calculatedSummaryAnswer()).should.eventually.contain('124.58')

        // Answers included in calculation should be shown
        .getText(NumberTotalPlaybackPage.fifthNumberAnswer()).should.eventually.contain('78.91')
        .getText(NumberTotalPlaybackPage.sixthNumberAnswer()).should.eventually.contain('45.67');
    });

    it('Given I confirm the total, When i get to the summary, Then I can complete the survey', function() {
      return browser
        .click(NumberTotalPlaybackPage.submit())
        .getUrl().should.eventually.contain(SummaryPage.pageName)
        .click(SummaryPage.submit())
        .getUrl().should.eventually.contain(ThankYouPage.pageName);
    });

  });
});
