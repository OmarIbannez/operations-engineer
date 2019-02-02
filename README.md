# Operations Engineering Project

## Project Overview

- Environment setup
- Bug fixes
- Automatic testing
- Implement new functionality
- Create UI

## Getting Started

- It is highly recommended to run all this from a \*nix terminal.
  If you don't have one currently set up, you can create an Ubuntu instance using [VirtualBox](https://www.virtualbox.org/wiki/Downloads) or [Docker](https://www.docker.com/).

- Initialize this repo in git.

- **Create an initial commit and push this code to a new repo on GitHub or GitLab.** This is extremely important. In order to show progress you must have this initial commit with the original project code in your own personal git repo.

- When you make additional commits, please include which problem you are working on in the commit message. (See more info below.)

- Use python2.7

- Install the requirements for the project. They're all found in requirements.txt. You'll probably
  want to use [pip](https://pypi.python.org/pypi/pip) for this.

- A sqlite3 db is used for this project. Run `build_or_refresh_db()` to populate it with the initial data.
  You might want to take a look at this data and the models before you get started.
  A SQLite Manager Add-On for Firefox or sqlitebrowser are simple options to view the db. However, the db browser you choose is unimportant.

- A little bit about the files and dirs in this project:

  - `runserver.py` will start the Flask server
  - `shell.py` is a terminal with all the accounting instances already imported
  - `accounting.models` contains the SQLAlchemy database models
  - `accounting.views` is the view for the Flask server
  - `accounting.utils` contains the PolicyAccounting class and bulk of the heavy lifting
  - `accounting.tests` contains the unit tests for PolicyAccounting

- Questions? Feel free to ask! Send an email to the BriteCore contact that sent you this project.

## Requirements

- Flask 0.9
- SQLAlchemy 0.7.9
- Flask-SQLAlchemy 0.16
- python-dateutil 1.5
- nose 1.1.2

## Helpful Links

- [Flask SQLAlchemy Plugin](http://pythonhosted.org/Flask-SQLAlchemy/)
- [SQLite Firefox Plugin](https://addons.mozilla.org/en-US/firefox/addon/sqlite-manager/)
- [SQLAlchemy Declarative Base](http://docs.sqlalchemy.org/en/rel_0_8/orm/extensions/declarative.html)
- [A List of Responsive Frameworks for HTML](http://komelin.com/en/5tips/5-most-popular-html5-responsive-frameworks)
- [Testing Flask](http://flask.pocoo.org/docs/testing/)
- [Knockout.js](http://knockoutjs.com/)
- [jQuery API](http://api.jquery.com/)
- [pip](https://pypi.python.org/pypi/pip)
- [flake8 (pep8 & syntax analyzer)](https://flake8.readthedocs.org/)
- [JS Hint](http://www.jshint.com/)

And some good things to know about writing Python:

- [PEP-8, a Style guide for Python](http://www.python.org/dev/peps/pep-0008/)
- [pudb, a full-screen, console-base, visual debugger for Python](https://pypi.python.org/pypi/pudb)
- [ipython, an enhanced interface to the Python interpreter](http://ipython.org/)

## The Problems

**Remember to put which problem you're working on in your commit message! Keep your commit history to 1-commit-per-problem and start each commit message with the number of the issue being solved.**

**NOTE: Populate your database. Run the following function in the shell: `build_or_refresh_db()` Any time you think that your db is getting messed up, you can run this again to start from scratch.**

1.  Policy Three (effective 1/1/2015) is on a monthly billing schedule.
    The team hasn't implemented monthly invoices yet.
    Please go ahead and implement that function without modifying the data
    so that Policy Three can have some invoices.

2.  Now that you've written monthly invoices, you should probably write a unit test for it.
    Use Python's built-in [unittest](https://docs.python.org/2/library/unittest.html) framework for this and run your tests with nosetests.

3.  Oh no, one of the test suites is completely failing! Figure out what caused this and fix it. Assume that it's a bug in the code and not in the test.

4.  Geez, whoever wrote PolicyAccounting sure didn't like making comments. Would you add
    some comments to the code and functions? You could even add some logging if you'd like.

5.  Mary Sue Client is having problems creating a new policy. Will you help her?
    The info is below:

        - Policy Number: 'Policy Four'
        - Effective: 2/1/2015
        - Billing Schedule: 'Two-Pay'
        - Named Insured: 'Ryan Bucket'
        - Agent: 'John Doe'
        - Annual Premium: $500

6.  The agent Bob Smith called Mary Sue Client furious because his insured, John Doe, couldn't
    pay off Policy One! Please help her out! _Hint: She tried the shell to make the payment_

7.  Did you notice that an invoice's cancel date is two weeks after the due date? For these two
    weeks, the policy's status is cancellation pending due to non-pay, but the system doesn't
    account for this in any way. If a policy is in cancellation pending due to non_pay, only an
    agent should be able to make a payment on it. There is a code stub for
    `evaluate_cancellation_pending_due_to_non_pay` to help get you started.

8.  You know what'd be great? Being able to change the billing schedule in the middle of a policy. Implement this schedule-changing functionality.
    For example, Policy Two is on quarterly and the insured (Anna White) has already paid off the
    first invoice. Making a payment for \$400 was kind of a stretch for her, so in the future she'd
    like to have monthly invoices. Those old quarterly invoices should be marked as deleted and switched
    over to a new billing schedule.

9.  Mary Sue Client doesn't like the way that cancelling a policy works. It doesn't do
    anything other than print to the screen! She thinks that maybe the Policy's status
    should change, and maybe even store the date that it cancelled. It might also be nice to
    be able to store a description about why the policy cancelled. Well, really she'd
    also like to be able to cancel policies for other reasons, like underwriting. Decide how
    to expand the cancellation logic and test it.

10. Mary Sue Client doesn't really like using the shell when she wants to
    look at policies and their invoices. Will you build her a view where she
    could look at it online? She wants to be able to enter a policy number
    and a date and be able to see the account balance and invoices (even the paid ones).
    There's already a Flask server, but if there's something that you'd rather use
    go ahead. Also, she wouldn't mind looking at a pretty display, but she'd rather
    it be more functional than pretty.

    The interface needs to be built with mobile devices in mind - so we recommend a responsive HTML/CSS
    framework that will do a lot of the work for you. We use [Bootstrap](http://getbootstrap.com/) at BriteCore -
    so it'd be a good choice.

    The interface should be hooked up with Knockout.js and be representative of good MVVM design.

11. Prevent any input errors with both Knockout validation & backend enforcement.

**BONUS**: If there's anything else bothering you about the code, go ahead and feel free to
change it. Make each additional update in its own commit and be sure to put "Bonus" in the commit message please. :)

## Questions?

If you have any questions, please send them to support-hires@britecore.com.

## Finished?

Once completed, please ensure your commit history in the repo is clean and understandable with a detailed view of your progress and changes from each problem.

When you are ready to submit the project, please add a link to your git repo to your cover letter and upload that and your resume to the [Operations Engineer application form](https://hire.withgoogle.com/public/jobs/britecorecom/view/P_AAAAAAEAADyEvJ6hdaW5No).
