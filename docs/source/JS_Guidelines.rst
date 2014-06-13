JavaScript Guidelines
=====================

General considerations
----------------------

-  this document is split in multiple sections

   -  general JavaScript
   -  TypeScript
   -  Angular

      -  Angular templates

   -  Adhocracy 3
   -  Tests

-  We prefer conventions set by 3rd party tools (e.g. `tslint`_) over our
   own preferences.
-  We try to be consistend with other guidelines from the adhocracy3
   project

General JavaScript
------------------

We follow most rules proposed by tslint (see tslint config for details).
However, there are some rules we want to adhere to that can not (yet) be
checked with tslint.

-  Use `strict mode`_ everywhere

   -  There seem to be multiple issues with strict mode and TypeScript

      -  http://typescript.codeplex.com/workitem/2003
      -  http://typescript.codeplex.com/workitem/2176

-  No implicit boolean conversions: ``if (typeof x === "undefined")`` instead
   of ``if (!x)``

-  Chaining is to be preferred.

   -  If chain elements are many lines long, it is ok to avoid
      chaining.  In this case, if chaining is used anyway, newlines and
      comments between chain elements are encouraged.

   -  Layout: Each function (also the first one) starts a new line.  The
      first line (without a ``.``) is indented at n+0, all functions at
      n+1 (4 spaces deeper).

-  Each new identfier has its own ``var``. (rationale: ``git diff`` / conflicts)

-  No whitespace immediately inside parentheses, brackets or braces (this
   includes empty blocks)::

       Yes: spam(ham[1], {eggs: 2})
       No:  spam( ham[ 1 ], { eggs: 2 } )

-  Do not align your code. Use the following indentation rules instead
   (single-line option is always allowed if reasonably short.):

   -  objects::

         foo = {
             a: 1,
             boeifj: 2,
             cfhe: 3
         }

   -  lists::

         foo = [
             138,
             281128
         ]

   -  function definitions::

          var foo(a : number) : number => a + 1;

          var foo = (arg : number) : void => {
              return;
          }

          var foo = (
              arg: number,
              otherarg: Class
          ) : void => {
              return;
          }

-  The last item in a list or in function parameters may by split across
   multiple lines::

       app.directive('myDirective', ["$q", "$http", ($q, $http) => {
           ...
       }]);

-  Do not use named functions. Assign anonymous functions to variables instead.
   This is less confusing. `Further reading
   <http://kangax.github.io/nfe/#expr-vs-decl>`_

-  If you need an alias for ``this``, always use ``self`` (as in knockout)
   or ``_self`` (in TypeScript classes).
   (``_this`` is used by TypeScript in compiled code and is disallowed
   in typescript source in e.g. class instance methods.)

   If more than one nested self is needed, re-assign outer ``self``\ s
   locally.

TypeScript
----------

-  imports at top

   -  standard libs first (if such a thing ever exists), then external
      modules, then a3-internal modules.

   -  only import from lower level.  (FIXME: "lower level" does not mean file
      directory hierarchy, but something to be clarified.  this rule
      is to be re-evaluated at some point.)

-  nested types are allowed up to 2 levels (``Foo<Bar<Baz>>``).  1
   level is to be preferred where possible.

-  Type functions, not the variables they are assigned to.

-  Use ``type[]`` rather than ``Array<type>``.

Lambdas
~~~~~~~

TypeScript has its own lambda syntax. It has two differences from
JavaScript's functions:

-  The result of the final statement is returned automatically.
-  ``this`` is the ``this`` from the enclosing scope.

Example::

    var lambda = () => {
        var nested_fn = function() {
             return this;
        };
        var nested_lambda = () => this;
    }

    var fn = function() {
        var nested_fn = function() {
             return this;
        };
        var nested_lambda = () => this;
    }

is compiled to::

    var _this = this;
    var lambda = function () {
        var nested_fn = function () {
            return this;
        };
        var nested_lambda = function () {
            return _this;
        };
    };

    var fn = function () {
        var _this = this;
        var nested_fn = function () {
            return this;
        };
        var nested_lambda = function () {
            return _this;
        };
    };

These lambdas *should always be preferred* over functions because
they avoid common mistakes like this::

    class Greeter {
        greeting = "Hello";

        greet = function() {
            alert(this.greeting);
        };
    }

    var greeter = new Greeter();
    setTimeout(greeter.greet, 1000);  // will alert 'undefined'

Still you should not use this behaviour extensively. Prefer to use
the explicit aliases ``_self`` and ``_class`` in class methods::

    class Greeter {
        public static greeting = "Hello";

        constructor(public name) {}

        greet = function() {
            var _self = this;
            var _class = (<any>_self).constructor;

            setTimeout(() => {
                console.log(_class.greeting + " " + _self.name + "!");
            }, 1000);
        }
    }

Angular
-------

-  prefer `isolated scope`_ in directives and pass in variables
   explicitly.

-  direct DOM manipulation/jQuery is only allowed inside directives.

-  dependency injection

   -  always use ``["$q", function($q) {…}]`` style

-  do not use ``$`` in your variable names (leave it to angular).

-  prefix

   -  directives: 'adh.*' for all directives declared in a3.  (in the
      future, this prefix may be split up in several ones, making
      refactoring necessary.  Client-specific prefices may be added
      without the need for refactoring.)

   -  service registration: '"adhHttp"'.  (services must be implemented
      so that they don't care if they are registered under another
      name.)

   -  service module import: 'import Http = require("Adhocracy/Services/Http");'.
      rationale: When using service modules, the fact that they provide
      services is obvious.

-  angular scopes must be typed with interfaces.

Template
~~~~~~~~

-  write
   `polyglot HTML5 <http://dev.w3.org/html5/html-author/#polyglot-documents>`_.

   -  prefix any angular-specific attributes with ``data-``::

         <span data-ng-bind="foo"></span>

   -  FIXME: include HTML checker for automated tests.

   -  Exception: The preferred way to use angular directives is the
      element syntax::

         <adh-proposal data-path="/adhocracy/proposal/1"></adh-proposal>

      -  This needs special care in IE8 and below. See
         https://docs.angularjs.org/guide/ie

-  prefer ``{{…}}`` over ``ngBind`` (except for root template).

-  FIXME: when to apply which classes (should be in balance with
   :doc:`CSS_Guidelines`)

   -  apply classes w/o a specific need/by default?

-  CSS and JavaScript are not allwed in templates.  This includes
   `ngStyle <https://docs.angularjs.org/api/ng/directive/ngStyle>`_.

-  Since templates (1) ideally are to be maintained by designers rather
   than software developers, and (2) are not type-checked by typescript,
   they must contain as little code as possible.


Documentation
~~~~~~~~~~~~~

-  Use `JSDoc`_-style comments in your code.

   -  Currently, no tool seems to be available to include JSDoc
      comments in sphinx.
   -  `TypeScript has only limited JSDoc support
      <http://typescript.codeplex.com/workitem/504>`_


.. _strict mode: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions_and_function_scope/Strict_mode
.. _tslint: https://github.com/palantir/tslint
.. _jsdoc: http://usejsdoc.org/
.. _isolated scope: https://docs.angularjs.org/guide/directive#isolating-the-scope-of-a-directive
